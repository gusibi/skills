#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith('--')) continue;
    const next = argv[i + 1];
    if (next && !next.startsWith('--')) {
      args[arg] = next;
      i += 1;
    } else {
      args[arg] = true;
    }
  }
  return args;
}

function toModelId(model) {
  return model
    .toLowerCase()
    .replace(/[\s_\/]+/g, '-')
    .replace(/[^a-z0-9.-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

function inferPricingType(m) {
  if (m.pricing_type) return m.pricing_type;
  if (m.input_price === 0 && m.output_price === 0) return 'free';
  if (m.input_price != null || m.output_price != null) return 'token';
  if (m.price != null) return m.price_unit ? `per_${m.price_unit}` : 'other';
  return 'unknown';
}

function flattenProviderData(data) {
  const rows = [];
  const { provider, url, currency, retrieved_at, models } = data;
  
  if (Array.isArray(models)) {
    for (const m of models) {
      const pricingType = inferPricingType(m);
      
      rows.push({
        provider,
        model_id: toModelId(m.model),
        model: m.model,
        pricing_type: pricingType,
        // Token pricing fields
        input_price: m.input_price ?? null,
        output_price: m.output_price ?? null,
        cache_price: m.cache_price ?? null,
        // Non-token pricing fields
        price: m.price ?? null,
        price_unit: m.price_unit ?? null,
        // Common fields
        context_length: m.context_length ?? null,
        currency,
        source_url: url,
        retrieved_at,
      });
    }
  }
  return rows;
}

function toCsv(rows) {
  const header = [
    'provider',
    'model_id',
    'model',
    'pricing_type',
    'input_price',
    'output_price',
    'cache_price',
    'price',
    'price_unit',
    'context_length',
    'currency',
    'source_url',
    'retrieved_at',
  ];

  const escape = (value) => {
    if (value == null) return '';
    const text = String(value);
    if (/[",\n]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
    return text;
  };

  const lines = [header.join(',')];
  for (const row of rows) {
    lines.push(header.map((key) => escape(row[key])).join(','));
  }
  return lines.join('\n') + '\n';
}

function run() {
  const args = parseArgs(process.argv);
  const inDir = args['--in-dir'] || 'prices';
  const outPath = args['--out'] || 'prices.json';
  const csvPath = args['--csv'] || 'prices.csv';

  if (!fs.existsSync(inDir)) {
    console.error(`Missing input directory: ${inDir}`);
    process.exit(1);
  }

  const entries = fs.readdirSync(inDir).filter((name) => name.endsWith('.json'));
  if (entries.length === 0) {
    console.error(`No JSON files found in ${inDir}`);
    process.exit(1);
  }

  const rows = [];
  for (const name of entries) {
    const raw = fs.readFileSync(path.join(inDir, name), 'utf8');
    const data = JSON.parse(raw);
    
    // Handle new nested format with provider.models array
    if (data.models && Array.isArray(data.models)) {
      rows.push(...flattenProviderData(data));
    }
    // Handle legacy flat array format
    else if (Array.isArray(data)) {
      rows.push(...data);
    }
  }

  fs.writeFileSync(outPath, JSON.stringify(rows, null, 2));
  if (csvPath) {
    fs.writeFileSync(csvPath, toCsv(rows));
  }

  // Summary by pricing type
  const byType = {};
  for (const r of rows) {
    byType[r.pricing_type] = (byType[r.pricing_type] || 0) + 1;
  }
  
  console.log(`Merged ${rows.length} records from ${entries.length} files into ${outPath}`);
  console.log(`  By pricing type: ${Object.entries(byType).map(([k, v]) => `${k}(${v})`).join(', ')}`);
  if (csvPath) console.log(`Saved CSV to ${csvPath}`);
}

run();

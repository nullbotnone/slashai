#!/usr/bin/env node
// post-typefully.js — Schedule a post via Typefully API v2
const https = require('https');
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const token = process.env.TYPEFULLY_API_KEY;
const text = process.argv[2];
const schedule = process.argv[3] || 'next-free-slot'; // "now", "next-free-slot", or ISO datetime

if (!text) {
  console.error('Usage: node post-typefully.cjs "tweet text" [schedule]');
  console.error('  schedule: "now", "next-free-slot", or ISO datetime');
  process.exit(1);
}

const postData = JSON.stringify({
  content: text,
  schedule_date: schedule,
});

const options = {
  hostname: 'api.typefully.com',
  path: '/v2/drafts',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': token,
    'Content-Length': Buffer.byteLength(postData),
  },
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    try {
      const result = JSON.parse(data);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        console.log('✅ Scheduled:', result.id || 'success');
        console.log('   Text:', text.substring(0, 80) + '...');
        console.log('   Schedule:', schedule);
      } else {
        console.error('❌ Error:', res.statusCode, JSON.stringify(result));
      }
    } catch (e) {
      console.error('❌ Response:', data);
    }
  });
});

req.on('error', (e) => console.error('❌ Error:', e.message));
req.write(postData);
req.end();

#!/usr/bin/env node
// post-buffer.js — Schedule a post via Buffer API
const https = require('https');

const token = process.env.BUFFER_TOKEN || 'fAdf8ZC4iYVUxZy574wNHr5LQYUBdfmujSkPHhM66Ix';
const text = process.argv[2];

if (!text) {
  console.error('Usage: node post-buffer.cjs "post text"');
  process.exit(1);
}

// First, get profile IDs
function getProfiles() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.bufferapp.com',
      path: '/1/profiles.json?access_token=' + token,
      method: 'GET',
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error('Failed to parse response: ' + data));
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

// Create a post
function createPost(profileId, text) {
  return new Promise((resolve, reject) => {
    const postData = new URLSearchParams({
      access_token: token,
      text: text,
      profile_ids: profileId,
    }).toString();

    const options = {
      hostname: 'api.bufferapp.com',
      path: '/1/updates/create.json',
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(postData),
      },
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error('Failed to parse: ' + data));
        }
      });
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

async function main() {
  try {
    // Get profiles
    const profiles = await getProfiles();
    if (profiles.error) {
      console.error('❌ Error getting profiles:', profiles.error);
      return;
    }

    if (!profiles || profiles.length === 0) {
      console.error('❌ No profiles found. Connect your X account in Buffer first.');
      return;
    }

    const profile = profiles[0];
    console.log('📱 Using profile:', profile.service, '@' + (profile.service_username || profile.service_id));

    // Create post
    const result = await createPost(profile.id, text);
    if (result.success) {
      console.log('✅ Post queued:', result.updates[0].id);
      console.log('   Text:', text.substring(0, 80) + '...');
    } else {
      console.error('❌ Error:', JSON.stringify(result));
    }
  } catch (err) {
    console.error('❌ Error:', err.message);
  }
}

main();

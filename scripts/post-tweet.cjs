#!/usr/bin/env node
// post-tweet.js — Post a tweet to X/Twitter
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const { TwitterApi } = require('twitter-api-v2');

const client = new TwitterApi({
  appKey: process.env.X_API_KEY,
  appSecret: process.env.X_API_SECRET,
  accessToken: process.env.X_ACCESS_TOKEN,
  accessSecret: process.env.X_ACCESS_TOKEN_SECRET,
});

const text = process.argv[2];

if (!text) {
  console.error('Usage: node post-tweet.js "tweet text"');
  process.exit(1);
}

async function post() {
  try {
    const rwClient = client.readWrite;
    const tweet = await rwClient.v2.tweet(text);
    console.log('✅ Posted:', tweet.data.id);
    console.log('   Text:', text.substring(0, 80) + '...');
  } catch (err) {
    console.error('❌ Error:', err.message || err);
    if (err.data) console.error('   Details:', JSON.stringify(err.data));
  }
}

post();

#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const CONFIG_FILE = path.join(__dirname, 'config.json');
const PLIST_FILE = path.join(process.env.HOME, 'Library/LaunchAgents/com.metricsTracker.plist');

async function askQuestion(question) {
  const script = `
    set response to text returned of (display dialog "${question.replace(/"/g, '\\"')}" default answer "" buttons {"OK"} default button "OK")
    return response
  `;
  const { stdout } = await execPromise(`osascript -e '${script}'`);
  return stdout.trim();
}

async function notify(title, message) {
  const script = `display notification "${message.replace(/"/g, '\\"')}" with title "${title.replace(/"/g, '\\"')}"`;
  await execPromise(`osascript -e '${script}'`);
}

async function setup() {
  try {
    await notify('Metrics Tracker Setup', 'Starting configuration...');
    
    const apiKey = await askQuestion('Enter your Anthropic API key:');
    
    if (!apiKey || apiKey.length < 10) {
      throw new Error('Invalid API key');
    }
    
    const config = {
      anthropicApiKey: apiKey,
      setupDate: new Date().toISOString()
    };
    
    await fs.writeFile(CONFIG_FILE, JSON.stringify(config, null, 2));
    await notify('Config Saved', '✓ API key configured');
    
    let nodePath;
    try {
      const { stdout } = await execPromise('which node');
      nodePath = stdout.trim();
    } catch {
      try {
        await execPromise('/opt/homebrew/bin/node --version');
        nodePath = '/opt/homebrew/bin/node';
      } catch {
        nodePath = '/usr/local/bin/node';
      }
    }
    
    const scriptPath = path.join(__dirname, 'metrics-tracker.js');
    
    const plistContent = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metricsTracker</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${nodePath}</string>
        <string>${scriptPath}</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Weekday</key>
            <integer>2</integer>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>30</integer>
        </dict>
        <dict>
            <key>Weekday</key>
            <integer>4</integer>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>30</integer>
        </dict>
    </array>
    
    <key>StandardOutPath</key>
    <string>${__dirname}/metrics-tracker.log</string>
    
    <key>StandardErrorPath</key>
    <string>${__dirname}/metrics-tracker.error.log</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>`;

    await fs.writeFile(PLIST_FILE, plistContent);
    await notify('Scheduler Created', '✓ launchd plist created');
    
    try {
      await execPromise(`launchctl unload ${PLIST_FILE} 2>/dev/null`);
    } catch {}
    
    await execPromise(`launchctl load ${PLIST_FILE}`);
    await notify('Scheduler Active', '✓ Metrics tracker will run Tue/Thu at 10:30');
    
    const testNow = await askQuestion('Test run now? (yes/no):');
    
    if (testNow.toLowerCase() === 'yes') {
      await notify('Test Run', 'Starting test collection...');
      require('./metrics-tracker.js').main();
    }
    
    await notify('Setup Complete! 🎉', 'Your autonomous metrics tracker is ready.');
    
    console.log(`
✅ Setup Complete!

Configuration:
- Script: ${scriptPath}
- Node: ${nodePath}
- Schedule: Tuesdays & Thursdays at 10:30 AM
- Data: ${__dirname}

To test manually:
  node ${scriptPath}

To view schedule:
  launchctl list | grep metricsTracker

To stop:
  launchctl unload ${PLIST_FILE}

To restart:
  launchctl load ${PLIST_FILE}
    `);
    
  } catch (error) {
    await notify('Setup Failed', error.message);
    console.error('Setup error:', error);
    process.exit(1);
  }
}

setup();

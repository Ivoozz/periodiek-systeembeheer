const readline = require('readline');
const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const ask = (question) => new Promise((resolve) => rl.question(question, resolve));

async function main() {
  console.log('\n--- OmniMail Interactive Setup ---\n');

  const port = await ask('Which port should OmniMail run on? (Default: 3000): ') || '3000';
  const url = await ask('What is the public URL of OmniMail? (e.g., http://mail.example.com): ') || `http://localhost:${port}`;
  
  console.log('\n[1/4] Generating .env file...');
  const nextAuthSecret = require('crypto').randomBytes(32).toString('hex');
  const envContent = `DATABASE_URL="file:./dev.db"
NEXTAUTH_URL="${url}"
NEXTAUTH_SECRET="${nextAuthSecret}"
PORT=${port}
`;
  fs.writeFileSync('.env', envContent);

  console.log('[2/4] Setting up Database...');
  try {
    execSync('npx prisma migrate dev --name init', { stdio: 'inherit' });
  } catch (error) {
    console.error('Database migration failed.', error.message);
  }

  console.log('[3/4] Building Next.js application...');
  try {
    execSync('npm run build', { stdio: 'inherit' });
  } catch (error) {
    console.error('Build failed.', error.message);
  }

  const createService = await ask('\n[4/4] Do you want to create a systemd service to run OmniMail automatically? (y/N): ');
  
  if (createService.toLowerCase() === 'y') {
    const cwd = process.cwd();
    const serviceContent = `[Unit]
Description=OmniMail Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${cwd}
ExecStart=/usr/bin/npm run start -- -p ${port}
Restart=on-failure
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
`;
    try {
      fs.writeFileSync('/etc/systemd/system/omnimail.service', serviceContent);
      execSync('systemctl daemon-reload', { stdio: 'inherit' });
      execSync('systemctl enable omnimail', { stdio: 'inherit' });
      execSync('systemctl start omnimail', { stdio: 'inherit' });
      console.log('Systemd service "omnimail" created and started.');
    } catch (err) {
      console.log('Could not set up systemd service automatically.', err.message);
    }
  }

  console.log('\n--- Setup Complete! ---');
  console.log(`You can access OmniMail at: ${url}`);
  rl.close();
}

main();

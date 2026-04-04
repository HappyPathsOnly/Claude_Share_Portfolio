import { execSync } from 'child_process';
import * as path from 'path';

export default async function globalSetup(): Promise<void> {
  const projectRoot = path.resolve(__dirname, '../..');
  console.log('\nRegenerating Bokeh HTML files (fetching live data)...');
  execSync('python generate_html.py', {
    cwd: projectRoot,
    stdio: 'inherit',
    // 5-minute ceiling — live data fetches for all funds + chart can be slow.
    timeout: 300_000,
  });
  console.log('HTML generation complete.\n');
}

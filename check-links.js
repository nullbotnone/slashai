const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

// Read all HTML files in the dist directory
const distDir = path.join(__dirname, 'dist');
const htmlFiles = [];

function findHtmlFiles(dir) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory()) {
      findHtmlFiles(filePath);
    } else if (filePath.endsWith('.html')) {
      htmlFiles.push(filePath);
    }
  });
}

findHtmlFiles(distDir);

console.log(`Found ${htmlFiles.length} HTML files to check`);

// Collect all internal links
const internalLinks = new Set();
const linkErrors = [];

htmlFiles.forEach(file => {
  try {
    const content = fs.readFileSync(file, 'utf8');
    const dom = new JSDOM(content);
    const document = dom.window.document;
    
    // Find all anchor tags with href attributes
    const links = document.querySelectorAll('a[href]');
    
    links.forEach(link => {
      const href = link.getAttribute('href');
      
      // Skip external links, mailto, tel, etc.
      if (href.startsWith('http') || 
          href.startsWith('mailto:') || 
          href.startsWith('tel:') ||
          href.startsWith('#')) {
        return;
      }
      
      // Normalize the link
      let normalized = href;
      if (normalized.endsWith('/')) {
        normalized = normalized.slice(0, -1);
      }
      if (!normalized.startsWith('/')) {
        normalized = '/' + normalized;
      }
      
      internalLinks.add(normalized);
    });
  } catch (error) {
    console.error(`Error processing ${file}:`, error.message);
  }
});

// Check if each internal link corresponds to an existing file
internalLinks.forEach(link => {
  // Remove leading slash and handle root path
  let filePath = link.substring(1);
  if (filePath === '') {
    filePath = 'index.html';
  } else if (!filePath.endsWith('.html')) {
    // Try as directory index
    filePath = path.join(filePath, 'index.html');
  }
  
  const fullPath = path.join(distDir, filePath);
  
  if (!fs.existsSync(fullPath)) {
    linkErrors.push({
      link: link,
      attemptedPath: fullPath
    });
  }
});

console.log(`Found ${internalLinks.size} unique internal links`);
console.log(`Found ${linkErrors.length} broken internal links`);

if (linkErrors.length > 0) {
  console.log('\nBroken links:');
  linkErrors.forEach(error => {
    console.log(`  ${error.link} -> ${error.attemptedPath}`);
  });
  process.exit(1);
} else {
  console.log('\n✓ All internal links are valid!');
  process.exit(0);
}
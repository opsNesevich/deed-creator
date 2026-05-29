const fs = require('fs');
const AdmZip = require('adm-zip');

function ensureMunicipality(m) {
  if (!m) return m;
  const suffixes = ['Township', 'Borough', 'City', 'Town', 'Village'];
  if (suffixes.some(function(s) { return m.trim().endsWith(s); })) return m.trim();
  return m.trim() + ' Township';
}

function fillDeedDocx(data, templatePath, outputPath) {
  const grantor     = data.grantor  || '';
  const grantor2    = data.grantor2 || '';
  const rel         = data.relationship || '';
  const fullGrantor = grantor2
    ? grantor + ' and ' + grantor2 + (rel ? ', ' + rel : '')
    : grantor;

  const signingDate   = data.signingDate || '';
  const trustDate     = data.trustDate || signingDate || '_____________, ______';
  const grantee       = data.newGrantee || '';

  const grantorAddr  = data.grantorAddr  || '';
  const municipality = ensureMunicipality(data.municipality || '');
  const county       = data.county || 'Burlington';
  const block        = data.block  || '';
  const lot          = data.lot    || '';
  const propAddr     = data.propAddr || grantorAddr;
  const certifyDate  = signingDate || '______________';

  const priorGrantees = data.priorGrantees    || fullGrantor;
  const priorDeedDate = data.priorDeedDate    || '';
  const priorRecorded = data.priorRecordedDate || '';
  // Claude returns 'priorCountyClerk' (e.g. "Burlington County Clerk's Office") — extract county name only
  const rawPriorClerk = data.priorCounty || data.priorCountyClerk || county;
  const priorCounty   = rawPriorClerk
    .replace(/\s*county\s*(clerk|register|of deeds).*/i, '')
    .replace(/\s*county\s*$/i, '')
    .trim() || county;
  const priorBook     = data.priorBook        || '';
  const priorPage     = data.priorPage        || '';
  const instrumentNo  = data.instrumentNo     || '';
  const instrumentStr = instrumentNo ? ', as Instrument No. ' + instrumentNo : '';

  const zip = new AdmZip(templatePath);
  let xml = zip.readAsText('word/document.xml');

  function replaceFirst(str, search, replacement) {
    const idx = str.indexOf(search);
    if (idx === -1) return str;
    return str.slice(0, idx) + replacement + str.slice(idx + search.length);
  }

  // ── Year cleanup ─────────────────────────────────────────────────────────────
  // Deed date line:    '_______________' + ', 20' + '2' + '6' + ','
  xml = xml.replace(
    /<w:t>, 20<\/w:t><\/w:r>[\s\S]*?<w:t>2<\/w:t><\/w:r>[\s\S]*?<w:t>6<\/w:t><\/w:r>[\s\S]*?<w:t>,<\/w:t>/,
    '<w:t>,</w:t>'
  );
  // Trust date line:   '_____________' + ', 202' + '6' + '.'
  xml = xml.replace(
    /<w:t>, 202<\/w:t><\/w:r>[\s\S]*?<w:t>6<\/w:t><\/w:r>[\s\S]*?<w:t>\.<\/w:t>/,
    '<w:t>.</w:t>'
  );
  // I CERTIFY date:    '______________' + ', 202' + '6' + ','
  xml = xml.replace(
    /<w:t>, 202<\/w:t><\/w:r>[\s\S]*?<w:t>6<\/w:t><\/w:r>[\s\S]*?<w:t>,<\/w:t>/,
    '<w:t>,</w:t>'
  );

  // ── Fill in document order (run numbers from template XML analysis) ───────────

  // 1. Deed date (run 2: 15 underscores)
  xml = replaceFirst(xml, '_______________', certifyDate);

  // 2. Grantor name (run 8: 28 underscores + comma)
  xml = replaceFirst(xml, '____________________________,', fullGrantor + ',');

  // 3. Grantor address (run 9: appended after 'whose address is')
  xml = replaceFirst(xml, 'whose address is</w:t>', 'whose address is ' + grantorAddr + '</w:t>');

  // 4. Grantee name (run 13: 27 underscores)
  xml = replaceFirst(xml, '___________________________', grantee);

  // 5. Trust date (run 15: 13 underscores; year suffix cleaned above)
  xml = replaceFirst(xml, '_____________', trustDate);

  // 6. Grantee address (runs 19+20: template splits 'whose address' / 'is ' across two XML runs)
  xml = xml.replace(
    '<w:t xml:space="preserve">is </w:t>',
    '<w:t xml:space="preserve"> is ' + grantorAddr + '</w:t>'
  );

  // 7. Tax Map municipality (run 37: 20 underscores)
  xml = replaceFirst(xml, '____________________', municipality);

  // 8. Tax Map county (run 40: 17 underscores)
  xml = replaceFirst(xml, '_________________', county);

  // 9. Tax Map Block No. (run 44: exact <w:t>____</w:t> — avoids matching inside run 48's 6-underscore prefix)
  xml = replaceFirst(xml, '<w:t>____</w:t>', '<w:t>' + block + '</w:t>');

  // 10. Tax Map Lot No. (run 47: 4 underscores + period — unique, run 48 has no '____.')
  xml = replaceFirst(xml, '____.', lot + '.');

  // 11. Property address
  xml = xml.replace(/street address of the property is:<\/w:t>/, 'street address of the property is: ' + propAddr + '</w:t>');
  xml = xml.replace(/street address of the property is: <\/w:t>/, 'street address of the property is: ' + propAddr + '</w:t>');

  // 12. Property section municipality (run 56: 15 underscores — 2nd occurrence after deed date)
  xml = replaceFirst(xml, '_______________', municipality);

  // 13. Property section county (run 61: 16 underscores — 1st occurrence)
  xml = replaceFirst(xml, '________________', county);

  // 14. NOTE section Lot (run 75: exact <w:t>____</w:t> — run 48 already consumed that prefix in step 9)
  xml = replaceFirst(xml, '<w:t>____</w:t>', '<w:t>' + lot + '</w:t>');

  // 15. NOTE section Block (run 78: exact <w:t>______</w:t> — run 48's prefix is now gone after step 9)
  xml = replaceFirst(xml, '<w:t>______</w:t>', '<w:t>' + block + '</w:t>');

  // 16. NOTE municipality (run 82: 16 underscores — 2nd occurrence after Property county)
  xml = replaceFirst(xml, '________________', municipality);

  // 17. NOTE county (run 84: 12 underscores — unique)
  xml = replaceFirst(xml, '____________', county);

  // 18. BEING prior grantees (run 89: 20 underscores — 2nd occurrence after Tax Map municipality)
  xml = replaceFirst(xml, '____________________', priorGrantees);

  // 19. BEING deed date (run 93: 15 underscores — 3rd occurrence)
  xml = replaceFirst(xml, '_______________', priorDeedDate);

  // 20. BEING recorded date (run 97: 16 underscores — 3rd occurrence)
  xml = replaceFirst(xml, '________________', priorRecorded);

  // 21. BEING county clerk (run 101: 11 underscores — template already has 'County Clerk/Register's Office' as fixed text after blank)
  xml = replaceFirst(xml, '___________', priorCounty);

  // 22. BEING deed book (run 110: 8 underscores — unique)
  xml = replaceFirst(xml, '________', priorBook);

  // 23. BEING page + instrument (run 115: 7 underscores — unique)
  xml = replaceFirst(xml, '_______', priorPage + instrumentStr);

  // 24. Signature line 1 grantor name (run 124)
  xml = replaceFirst(xml, 'CLIENT NAME', grantor);

  // 25. Signature line 2 co-grantor name (run 127)
  xml = replaceFirst(xml, 'CLIENT NAME', grantor2 || '');

  // 26. I CERTIFY date (run 134: exact <w:t>______________</w:t> — avoids matching inside 31-underscore signature blank lines that precede this section)
  xml = replaceFirst(xml, '<w:t>______________</w:t>', '<w:t>' + certifyDate + '</w:t>');

  // 27. I CERTIFY grantor 1 (run 139)
  xml = replaceFirst(xml, 'CLIENT NAME', grantor);

  // 28. I CERTIFY grantor 2 (run 143)
  xml = replaceFirst(xml, 'CLIENT NAME', grantor2 || grantor);

  // 29. County references throughout
  xml = xml.split('County of Burlington').join('County of ' + county);

  zip.updateFile('word/document.xml', Buffer.from(xml, 'utf-8'));
  zip.writeZip(outputPath);
}

module.exports = { fillDeedDocx };

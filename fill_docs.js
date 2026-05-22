const fs = require('fs');
const AdmZip = require('adm-zip');

function ensureMunicipality(m) {
  if (!m) return m;
  const suffixes = ['Township', 'Borough', 'City', 'Town', 'Village'];
  if (suffixes.some(s => m.trim().endsWith(s))) return m.trim();
  return m.trim() + ' Township';
}

function fillDeedDocx(data, templatePath, outputPath) {
  const grantor     = data.grantor  || '';
  const grantor2    = data.grantor2 || '';
  const rel         = data.relationship || '';
  const fullGrantor = grantor2
    ? `${grantor} and ${grantor2}${rel ? ', ' + rel : ''}`
    : grantor;

  const signingDate   = data.signingDate || '';
  const trustDate     = data.trustDate || signingDate || '_____________, ______';
  const grantee       = data.newGrantee || '';
  const granteeClause = grantee ? `${grantee}, a Trust, dated ${trustDate}` : `___________________________, a Trust, dated ${trustDate}`;

  const grantorAddr  = data.grantorAddr  || '';
  const municipality = ensureMunicipality(data.municipality || '');
  const county       = data.county || 'Burlington';
  const block        = data.block  || '';
  const lot          = data.lot    || '';
  const propAddr     = data.propAddr || grantorAddr;
  const certifyDate  = signingDate || '______________';

  const priorGrantees    = data.priorGrantees    || '';
  const priorDeedDate    = data.priorDeedDate    || '';
  const priorRecorded    = data.priorRecordedDate || '';
  const priorCounty      = data.priorCounty      || county;
  const priorBook        = data.priorBook        || '';
  const priorPage        = data.priorPage        || '';
  const instrumentNo     = data.instrumentNo     || '';
  const instrumentStr    = instrumentNo ? `, as Instrument No. ${instrumentNo}` : '';

  const zip = new AdmZip(templatePath);
  let xml = zip.readAsText('word/document.xml');

  function replaceFirst(str, search, replacement) {
    const idx = str.indexOf(search);
    if (idx === -1) return str;
    return str.slice(0, idx) + replacement + str.slice(idx + search.length);
  }

  // Fix: remove the hardcoded year fragments ", 202" and "6" that follow trust date
  // These appear as separate runs in the template: ', 202' + '6' + '.'
  xml = xml.replace(/<w:t>, 202<\/w:t><\/w:r>.*?<w:r[^>]*><w:rPr>.*?<\/w:rPr><w:t>6<\/w:t>/s, '<w:t></w:t></w:r><w:r><w:rPr></w:rPr><w:t>');
  // Simpler fallback: just replace the text content
  xml = xml.replace(/>_, 202<\/w:t>/, '>_</w:t>');

  // 1. Deed date
  xml = replaceFirst(xml, '_______________', certifyDate);
  // 2. Grantor name (has trailing comma in template)
  xml = replaceFirst(xml, '____________________________,', `${fullGrantor},`);
  // 3. Grantee / trust name
  xml = replaceFirst(xml, '___________________________', grantee || '___________________________');
  // Fix: replace ", a Trust, dated " + trust date placeholder separately
  xml = replaceFirst(xml, '_____________', trustDate);
  // 4. Remove stray year ", 2026" or ", 202" + "6" from template
  xml = xml.replace(/<w:t xml:space="preserve">, 202<\/w:t><\/w:r><w:r[^>]*><w:t>6<\/w:t>/g, '<w:t></w:t></w:r><w:r><w:t>');
  xml = xml.replace(/, 202\s*6\s*\./g, '.');

  // 5. Grantee address (same as grantor)
  // 6. Tax map municipality
  xml = replaceFirst(xml, '____________________', municipality);
  // 7. Tax map county
  xml = replaceFirst(xml, '_________________', county);
  // 8. Block
  xml = replaceFirst(xml, '____', block);
  // 9. Lot (has period after)
  xml = replaceFirst(xml, '____.', `${lot}.`);
  // 10. Property address
  xml = xml.replace(/street address of the property is:<\/w:t>/,
    `street address of the property is: ${propAddr}</w:t>`);
  xml = xml.replace(/street address of the property is: <\/w:t>/,
    `street address of the property is: ${propAddr}</w:t>`);
  // 11. Grantor address
  xml = xml.replace(/whose address<\/w:t><\/w:r><w:r[^>]*><w:t[^>]*>is /,
    `whose address</w:t></w:r><w:r><w:t xml:space="preserve">is ${grantorAddr} `);
  // 12. NOTE line municipality
  xml = replaceFirst(xml, '________________', municipality);
  // 13. NOTE line county
  xml = replaceFirst(xml, '____________', county);
  // 14. BEING prior grantees
  xml = replaceFirst(xml, '____________________', priorGrantees || fullGrantor);
  // 15. BEING deed date
  xml = replaceFirst(xml, '_______________', priorDeedDate);
  // 16. BEING recorded date
  xml = replaceFirst(xml, '________________', priorRecorded);
  // 17. BEING county clerk
  xml = replaceFirst(xml, '___________', `${priorCounty} County Clerk/Register's Office`);
  // 18. BEING deed book
  xml = replaceFirst(xml, '________', priorBook);
  // 19. BEING page + instrument
  xml = replaceFirst(xml, '_______', priorPage + instrumentStr);
  // 20. Signature line 1
  xml = replaceFirst(xml, 'CLIENT NAME', grantor);
  // 21. Signature line 2
  xml = replaceFirst(xml, 'CLIENT NAME', grantor2 || '');
  // 22. I CERTIFY date
  xml = replaceFirst(xml, '______________', certifyDate);
  // 23. I CERTIFY grantor 1
  xml = replaceFirst(xml, 'CLIENT NAME', grantor);
  // 24. I CERTIFY grantor 2
  xml = replaceFirst(xml, 'CLIENT NAME', grantor2 || grantor);
  // 25. County of Burlington → actual county
  xml = xml.split('County of Burlington').join(`County of ${county}`);
  xml = xml.split('BURLINGTON').join(county.toUpperCase());

  zip.updateFile('word/document.xml', Buffer.from(xml, 'utf-8'));
  zip.writeZip(outputPath);
}

module.exports = { fillDeedDocx };

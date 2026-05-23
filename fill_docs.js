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
  const priorCounty   = data.priorCounty      || county;
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

  // Remove stray year runs: ', 20' + '2' + '6' + ','
  xml = xml.replace(
    /<w:t>, 20<\/w:t><\/w:r>[\s\S]*?<w:t>2<\/w:t><\/w:r>[\s\S]*?<w:t>6<\/w:t><\/w:r>[\s\S]*?<w:t>,<\/w:t>/,
    '<w:t>,</w:t>'
  );

  // 1. Deed date
  xml = replaceFirst(xml, '_______________', certifyDate);

  // 2. Grantor name (template has '____________________________,' with comma)
  xml = replaceFirst(xml, '____________________________,', fullGrantor + ',');

  // 3. Grantor address
  xml = replaceFirst(xml, 'whose address is</w:t>', 'whose address is ' + grantorAddr + '</w:t>');

  // 4. Grantee name ONLY — template already has ', a Trust, dated ' as fixed text after
  xml = replaceFirst(xml, '___________________________', grantee);

  // 5. Trust date — replaces '_____________' (the date placeholder after ', a Trust, dated ')
  xml = replaceFirst(xml, '_____________', trustDate);

  // 6. Grantee address
  xml = replaceFirst(xml, 'whose address is</w:t>', 'whose address is ' + grantorAddr + '</w:t>');

  // 7. Tax map municipality
  xml = replaceFirst(xml, '____________________', municipality);

  // 8. Tax map county
  xml = replaceFirst(xml, '_________________', county);

  // 9. Block
  xml = replaceFirst(xml, '____', block);

  // 10. Lot
  xml = replaceFirst(xml, '____.', lot + '.');

  // 11. Property address
  xml = xml.replace(/street address of the property is:<\/w:t>/, 'street address of the property is: ' + propAddr + '</w:t>');
  xml = xml.replace(/street address of the property is: <\/w:t>/, 'street address of the property is: ' + propAddr + '</w:t>');

  // 12. NOTE line municipality
  xml = replaceFirst(xml, '________________', municipality);

  // 13. NOTE line county
  xml = replaceFirst(xml, '____________', county);

  // 14. BEING prior grantees
  xml = replaceFirst(xml, '____________________', priorGrantees);

  // 15. BEING deed date
  xml = replaceFirst(xml, '_______________', priorDeedDate);

  // 16. BEING recorded date
  xml = replaceFirst(xml, '________________', priorRecorded);

  // 17. BEING county clerk
  xml = replaceFirst(xml, '___________', priorCounty + " County Clerk/Register's Office");

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

  // 25. County references
  xml = xml.split('County of Burlington').join('County of ' + county);

  zip.updateFile('word/document.xml', Buffer.from(xml, 'utf-8'));
  zip.writeZip(outputPath);
}

module.exports = { fillDeedDocx };

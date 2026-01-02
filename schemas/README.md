# CDISC Schemas

This directory should contain the official CDISC define-xml schema files.

## Required Files

- `define-xml-2.1.xsd` - Define-XML 2.1 Schema
- `ODM1-3-2.xsd` - ODM 1.3.2 Schema (dependency)

## Download Instructions

### Option 1: Using wget (Linux/Mac)

```bash
wget -O schemas/define-xml-2.1.xsd \
  https://www.cdisc.org/sites/default/files/2021-09/define-xml-2.1.xsd

wget -O schemas/ODM1-3-2.xsd \
  https://www.cdisc.org/sites/default/files/ODM1-3-2/ODM1-3-2.xsd
```

### Option 2: Using curl

```bash
curl -o schemas/define-xml-2.1.xsd \
  https://www.cdisc.org/sites/default/files/2021-09/define-xml-2.1.xsd

curl -o schemas/ODM1-3-2.xsd \
  https://www.cdisc.org/sites/default/files/ODM1-3-2/ODM1-3-2.xsd
```

### Option 3: Manual Download

1. Visit [CDISC Define-XML Page](https://www.cdisc.org/standards/data-exchange/define-xml)
2. Download Define-XML 2.1 Schema
3. Save as `schemas/define-xml-2.1.xsd`
4. Download ODM 1.3.2 Schema (if referenced)
5. Save as `schemas/ODM1-3-2.xsd`

## Notes

- Schema files are **not** included in the repository due to licensing
- You must download them separately before running validation
- These schemas are maintained by CDISC and subject to their terms of use
- Always use the official CDISC schemas for production validation

## Version Information

- **Define-XML Version**: 2.1.0
- **ODM Version**: 1.3.2
- **Last Updated**: January 2026

For the latest schema versions, visit: https://www.cdisc.org/standards

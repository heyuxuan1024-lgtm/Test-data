# Prompt index

Condition A = underspecified (only the source code is given).
Condition B = A plus module name, exact import statement, no-reimplementation
rule and a fixed test filename.

| module | lines | expected test file | import used in condition B | 粘贴保存到 |
|---|---|---|---|---|
| itsdangerous.encoding | 54 | `test_itsdangerous_encoding.py` | `from itsdangerous import encoding` | `generated/<模型>/<条件>/itsdangerous_encoding.py` |
| humanize.filesize | 110 | `test_humanize_filesize.py` | `from humanize import filesize` | `generated/<模型>/<条件>/humanize_filesize.py` |
| stdnum.iban | 135 | `test_stdnum_iban.py` | `from stdnum import iban` | `generated/<模型>/<条件>/stdnum_iban.py` |
| base58 | 159 | `test_base58.py` | `import base58` | `generated/<模型>/<条件>/base58.py` |
| stdnum.isbn | 207 | `test_stdnum_isbn.py` | `from stdnum import isbn` | `generated/<模型>/<条件>/stdnum_isbn.py` |
| stringcase | 247 | `test_stringcase.py` | `import stringcase` | `generated/<模型>/<条件>/stringcase.py` |
| inflection | 426 | `test_inflection.py` | `import inflection` | `generated/<模型>/<条件>/inflection.py` |
| humanize.number | 569 | `test_humanize_number.py` | `from humanize import number` | `generated/<模型>/<条件>/humanize_number.py` |
| semver.version | 878 | `test_semver_version.py` | `from semver import version` | `generated/<模型>/<条件>/semver_version.py` |
| packaging.version | 1252 | `test_packaging_version.py` | `from packaging import version` | `generated/<模型>/<条件>/packaging_version.py` |

Total: 10 modules x 2 conditions = 20 prompt files.

`generated/` 下已建好全部 placeholder（3 模型 × 2 条件 × 15 模块 = 90 个空文件），
把模型返回的代码直接粘进对应文件保存即可，不要改动代码内容。

# UTF-8 repair plan

Use an ASCII-only SQL wrapper with PostgreSQL Unicode escapes, within the single future transaction. Update only `subjects.name`, selected by unchanged `code`:

- ALG: `U&'\\00C1lgebra Lineal'`
- ALG-ELEM: `U&'\\00C1lgebra Elemental / Prec\\00E1lculo'`
- EST: `U&'Estad\\00EDstica'`
- CALC-DIF: `U&'C\\00E1lculo Diferencial'`
- CALC-INT: `U&'C\\00E1lculo Integral'`

Validate UTF-8 hex exactly: ALG `c3816c6765627261204c696e65616c`; ALG-ELEM `c3816c676562726120456c656d656e74616c202f2050726563c3a16c63756c6f`; EST `4573746164c3ad7374696361`; CALC-DIF `43c3a16c63756c6f204469666572656e6369616c`; CALC-INT `43c3a16c63756c6f20496e74656772616c`.

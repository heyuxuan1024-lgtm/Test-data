import pytest
import math
from humanize.number import (
    _format_not_finite,
    ordinal,
    intcomma,
    intword,
    apnumber,
    fractional,
    scientific,
    clamp,
    metric,
)

def test_format_not_finite():
    assert _format_not_finite(float('nan')) == 'NaN'
    assert _format_not_finite(float('-inf')) == '-Inf'
    assert _format_not_finite(float('inf')) == '+Inf'
    assert _format_not_finite(1.0) == ''

def test_ordinal():
    assert ordinal(1) == '1st'
    assert ordinal(2) == '2nd'
    assert ordinal(3) == '3rd'
    assert ordinal(4) == '4th'
    assert ordinal(11) == '11th'
    assert ordinal(12) == '12th'
    assert ordinal(13) == '13th'
    assert ordinal(21) == '21st'
    assert ordinal(101) == '101st'
    assert ordinal(111) == '111th'
    assert ordinal(1002) == '1002nd'
    assert ordinal(1.0) == '1st'
    assert ordinal('2') == '2nd'
    assert ordinal('invalid') == 'invalid'
    assert ordinal(float('nan')) == 'NaN'
    assert ordinal(1, gender='female') == '1st'

def test_intcomma():
    assert intcomma(100) == '100'
    assert intcomma(1000) == '1,000'
    assert intcomma(1000000) == '1,000,000'
    assert intcomma(1234567.25) == '1,234,567.25'
    assert intcomma(1234.5454545, 2) == '1,234.55'
    assert intcomma(14308.40, 1) == '14,308.4'
    assert intcomma("14308.40", 1) == '14,308.4'
    assert intcomma("1000") == '1,000'
    assert intcomma(None) == 'None'
    assert intcomma(float('inf')) == '+Inf'
    assert intcomma("invalid") == 'invalid'

def test_intword():
    assert intword(100) == '100'
    assert intword(12400) == '12.4 thousand'
    assert intword(1000000) == '1.0 million'
    assert intword(1200000000) == '1.2 billion'
    assert intword(-1000000) == '-1.0 million'
    assert intword(8100000000000000000000000000000000) == '8.1 decillion'
    assert intword(10**100) == '1.0 googol'
    assert intword("1234000", "%0.3f") == '1.234 million'
    assert intword(None) == 'None'
    assert intword(float('nan')) == 'NaN'
    assert intword("invalid") == 'invalid'
    assert intword(999999) == '1.0 million'

def test_apnumber():
    assert apnumber(0) == 'zero'
    assert apnumber(5) == 'five'
    assert apnumber(9) == 'nine'
    assert apnumber(10) == '10'
    assert apnumber("7") == 'seven'
    assert apnumber("foo") == 'foo'
    assert apnumber(None) == 'None'
    assert apnumber(float('inf')) == '+Inf'

def test_fractional():
    assert fractional(0.3) == '3/10'
    assert fractional(1.3) == '1 3/10'
    assert fractional(1/3) == '1/3'
    assert fractional(1) == '1'
    assert fractional(-1.3) == '-1 3/10'
    assert fractional("ten") == 'ten'
    assert fractional(None) == 'None'
    assert fractional(float('nan')) == 'NaN'

def test_scientific():
    assert scientific(0.3) == '3.00 x 10⁻¹'
    assert scientific(500) == '5.00 x 10²'
    assert scientific(-1000) == '-1.00 x 10³'
    assert scientific(1000, 1) == '1.0 x 10³'
    assert scientific("99") == '9.90 x 10¹'
    assert scientific("foo") == 'foo'
    assert scientific(None) == 'None'
    assert scientific(float('inf')) == '+Inf'

def test_clamp():
    assert clamp(123.456) == '123.456'
    assert clamp(0.0001, floor=0.01) == '<0.01'
    assert clamp(0.99, format="{:.0%}", ceil=0.99) == '99%'
    assert clamp(0.999, format="{:.0%}", ceil=0.99) == '>99%'
    assert clamp(1, format=intword, floor=1e6, floor_token="under ") == 'under 1.0 million'
    assert clamp(None) is None
    assert clamp(float('nan')) == 'NaN'
    with pytest.raises(ValueError, match="Invalid format"):
        clamp(10, format=123)

def test_metric():
    assert metric(1500, "V") == '1.50 kV'
    assert metric(2e8, "W") == '200 MW'
    assert metric(220e-6, "F") == '220 μF'
    assert metric(1e-14, precision=4) == '10.00 f'
    assert metric(0, "m") == '0.00 m'
    assert metric(1e40) == '1.00 x 10⁴⁰'
    assert metric(float('inf')) == '+Inf'
    assert metric(999, "g", precision=3) == '999 g'
    assert metric(1500, "°") == '1.50k°'
import pytest
from humanize import number

def test_format_not_finite():
    assert number._format_not_finite(float('nan')) == 'NaN'
    assert number._format_not_finite(float('-inf')) == '-Inf'
    assert number._format_not_finite(float('inf')) == '+Inf'
    assert number._format_not_finite(1.0) == ''

def test_ordinal():
    assert number.ordinal(1) == '1st'
    assert number.ordinal(2) == '2nd'
    assert number.ordinal(3) == '3rd'
    assert number.ordinal(4) == '4th'
    assert number.ordinal(11) == '11th'
    assert number.ordinal(12) == '12th'
    assert number.ordinal(13) == '13th'
    assert number.ordinal(21) == '21st'
    assert number.ordinal(101) == '101st'
    assert number.ordinal(111) == '111th'
    assert number.ordinal(1002) == '1002nd'
    assert number.ordinal(1.0) == '1st'
    assert number.ordinal('2') == '2nd'
    assert number.ordinal('invalid') == 'invalid'
    assert number.ordinal(float('nan')) == 'NaN'
    assert number.ordinal(1, gender='female') == '1st'

def test_intcomma():
    assert number.intcomma(100) == '100'
    assert number.intcomma(1000) == '1,000'
    assert number.intcomma(1000000) == '1,000,000'
    assert number.intcomma(1234567.25) == '1,234,567.25'
    assert number.intcomma(1234.5454545, 2) == '1,234.55'
    assert number.intcomma(14308.40, 1) == '14,308.4'
    assert number.intcomma("14308.40", 1) == '14,308.4'
    assert number.intcomma("1000") == '1,000'
    assert number.intcomma(None) == 'None'
    assert number.intcomma(float('inf')) == '+Inf'
    assert number.intcomma("invalid") == 'invalid'

def test_intword():
    assert number.intword(100) == '100'
    assert number.intword(12400) == '12.4 thousand'
    assert number.intword(1000000) == '1.0 million'
    assert number.intword(1200000000) == '1.2 billion'
    assert number.intword(-1000000) == '-1.0 million'
    assert number.intword(8100000000000000000000000000000000) == '8.1 decillion'
    assert number.intword(10**100) == '1.0 googol'
    assert number.intword("1234000", "%0.3f") == '1.234 million'
    assert number.intword(None) == 'None'
    assert number.intword(float('nan')) == 'NaN'
    assert number.intword("invalid") == 'invalid'
    assert number.intword(999999) == '1.0 million'

def test_apnumber():
    assert number.apnumber(0) == 'zero'
    assert number.apnumber(5) == 'five'
    assert number.apnumber(9) == 'nine'
    assert number.apnumber(10) == '10'
    assert number.apnumber("7") == 'seven'
    assert number.apnumber("foo") == 'foo'
    assert number.apnumber(None) == 'None'
    assert number.apnumber(float('inf')) == '+Inf'

def test_fractional():
    assert number.fractional(0.3) == '3/10'
    assert number.fractional(1.3) == '1 3/10'
    assert number.fractional(1/3) == '1/3'
    assert number.fractional(1) == '1'
    assert number.fractional(-1.3) == '-1 3/10'
    assert number.fractional("ten") == 'ten'
    assert number.fractional(None) == 'None'
    assert number.fractional(float('nan')) == 'NaN'

def test_scientific():
    assert number.scientific(0.3) == '3.00 x 10⁻¹'
    assert number.scientific(500) == '5.00 x 10²'
    assert number.scientific(-1000) == '-1.00 x 10³'
    assert number.scientific(1000, 1) == '1.0 x 10³'
    assert number.scientific("99") == '9.90 x 10¹'
    assert number.scientific("foo") == 'foo'
    assert number.scientific(None) == 'None'
    assert number.scientific(float('inf')) == '+Inf'

def test_clamp():
    assert number.clamp(123.456) == '123.456'
    assert number.clamp(0.0001, floor=0.01) == '<0.01'
    assert number.clamp(0.99, format="{:.0%}", ceil=0.99) == '99%'
    assert number.clamp(0.999, format="{:.0%}", ceil=0.99) == '>99%'
    assert number.clamp(1, format=number.intword, floor=1e6, floor_token="under ") == 'under 1.0 million'
    assert number.clamp(None) is None
    assert number.clamp(float('nan')) == 'NaN'
    with pytest.raises(ValueError, match="Invalid format"):
        number.clamp(10, format=123)

def test_metric():
    assert number.metric(1500, "V") == '1.50 kV'
    assert number.metric(2e8, "W") == '200 MW'
    assert number.metric(220e-6, "F") == '220 μF'
    assert number.metric(1e-14, precision=4) == '10.00 f'
    assert number.metric(0, "m") == '0.00 m'
    assert number.metric(1e40) == '1.00 x 10⁴⁰'
    assert number.metric(float('inf')) == '+Inf'
    assert number.metric(999, "g", precision=3) == '999 g'
    assert number.metric(1500, "°") == '1.50k°'
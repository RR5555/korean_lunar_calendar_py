"""Library to convert between Solar and Lunar dates.

Modified from:
KoreanLunarCalendar [korean_lunar_calendar/korean_lunar_calendar.py](https://github.com/usingsky/korean_lunar_calendar_py/blob/master/korean_lunar_calendar/korean_lunar_calendar.py)
Here is a library to convert Korean lunar-calendar to Gregorian calendar.
Korean calendar and Chinese calendar is same lunar calendar but have different date.
This follow the KARI(Korea Astronomy and Space Science Institute)
@author : usingsky@gmail.com
MIT Licence

---

To Gregorian proleptic calendar.

By:
@author : https://github.com/RR5555
"""

from typing import Final, Annotated, Any
from pydantic import BaseModel, Field, validate_call, dataclasses
# from typing import get_type_hints, get_origin, get_args


# ruff: noqa: PLR2004

# @dataclasses.dataclass()
class KoreanLunarCalendar() :
	r"""Handle lunar calendar from 1000-02-13 (solar calendar) to 2050-12-31 (solar calendar) by fetching data from look-up tables.

	The lunar data is in the form:

	`|1X00|00XX|XXXX|XXXX|XXXX|XXXX|XXXX|XXXX|`

	Where:

	|Bits|Desc.|
	|:---|:---|
	|`\|1.00\|00..\|....\|....\|....\|....\|....\|....\|`|
	|`\|.X..\|....\|....\|....\|....\|....\|....\|....\|`|Indicates (`X` bit) solar intercalation year (or not if `False`)|
	|`\|....\|..XX\|XXXX\|XXX.\|....\|....\|....\|....\|`|Year duration in days (on 9 bits, for a max of up to 511 days)|
	|`\|....\|....\|....\|...X\|....\|....\|....\|....\|`|Indicates (`X` bit) if the intercalation month lasts 30 days (or 29 if `False`)|
	|`\|....\|....\|....\|....\|XXXX\|....\|....\|....\|`|Lunar intercalation month (`0bXXXX`)|
	|
	|`\|....\|....\|....\|....\|....\|YYYY\|YYYY\|YYYY\|`|For each non-intercalation month (from 1(leftmost `Y` bit) to 12(rightmost `Y` bit)), indicates if it lasts 30 days (or 29 if `False`)|

	Examples:

	---

	2022: 0x82c60ad5

	0b1000_0010_1100_0110_0000_1010_1101_0101

	Year duration (days): 0b10_1100_011: 355
	
	Solar intercalation year: No
	
	|Month|0|1|2|3|4|5|6|7|8|9|10|11|12|
	|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
	|**Y**                           |    |1 |0 |1 |0 |1 |1 |0 |1 |0 |1 |0 |1 |
	|**Duration (days)**             |[29]|30|29|30|29|30|30|29|30|29|30|29|30|
	|**Lunar intercalation month**   |X   |  |  |  |  |  |  |  |  |  |  |  |  |

	Year duration calculation: [29]+30*(7)+29*(5)=[29]+30*12-5=[29]+355
	
	---


	2025: 0x83006a6e

	0b1000_0011_0000_0000_0110_1010_0110_1110

	Year duration (days): 0b11_0000_000: 384

	Solar intercalation year: No
	
	|Month                           |0   |1 |2 |3 |4 |5 |6     |7 |8 |9 |10|11|12|
	|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
	|**Y**                           |    |1 |0 |1 |0 |0 |1     |1 |0 |1 |1 |1 |0 |
	|**Duration (days)**             |    |30|29|30|29|29|30[29]|30|29|30|30|30|29|
	|**Lunar intercalation month**   |    |  |  |  |  |  |X     |  |  |  |  |  |  |

	Year duration calculation: [29]+30*(7)+29*(5)=[29]+30*12-5=[29]+355=384

	From [Hong Kong Observatory -- Gregorian-Lunar Calendar Conversion Table of 2025 (Yi-si year of the Snake)](https://www.hko.gov.hk/en/gts/time/calendar/pdf/files/2025e.pdf): 6 month: 30 days then 29 days

	---

	For a lunar month, when an intercalation month happens: First, the normal month duration occurs, then the intercaltion month duration occurs. In effect, lunar year where an intercalation month happens, will have 13 months (12 regulars + one intercalation).


	"""

	KOREAN_LUNAR_MIN_VALUE: Final[int] = 10000101
	KOREAN_LUNAR_MAX_VALUE: Final[int] = 20501118
	# Lunar: 1000/01/01 -> Solar: 1000/02/13 (44th day of the year) => 43 days diff.
	KOREAN_SOLAR_MIN_VALUE: Final[int] = 10000213
	KOREAN_SOLAR_MAX_VALUE: Final[int] = 20501231

	KOREAN_LUNAR_BASE_YEAR: Final[int] = 1000
	SOLAR_LUNAR_DAY_DIFF: Final[int] = 43

	# Lunar month duration is between 29 & 30 days
	LUNAR_SMALL_MONTH_DAY: Final[int] = 29
	LUNAR_BIG_MONTH_DAY: Final[int] = 30
	SOLAR_SMALL_YEAR_DAY: Final[int] = 365
	SOLAR_BIG_YEAR_DAY: Final[int] = 366

	# Duration of solar month (from Jan. to Dec. + extra Feb. long version)
	SOLAR_DAYS: Final[tuple[int, ...]] = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 29)

	# Cheongan 10 year cycles, ganji 12 year cycle
	KOREAN_CHEONGAN: Final[tuple[int, ...]] = (0xac11, 0xc744, 0xbcd1, 0xc815, 0xbb34, 0xae30, 0xacbd, 0xc2e0, 0xc784, 0xacc4) # 10
	KOREAN_GANJI: Final[tuple[int, ...]] = (0xc790, 0xcd95, 0xc778, 0xbb18, 0xc9c4, 0xc0ac, 0xc624, 0xbbf8, 0xc2e0, 0xc720, 0xc220, 0xd574) # 12
	KOREAN_GAPJA_UNIT: Final[tuple[int, ...]] = (0xb144, 0xc6d4, 0xc77c) # 3 년, 월, 일: year, month, day in korean

	CHINESE_CHEONGAN: Final[tuple[int, ...]] = (0x7532, 0x4e59, 0x4e19, 0x4e01, 0x620a, 0x5df1, 0x5e9a, 0x8f9b, 0x58ec, 0x7678) # 10
	CHINESE_GANJI: Final[tuple[int, ...]] = (0x5b50, 0x4e11, 0x5bc5, 0x536f, 0x8fb0, 0x5df3, 0x5348, 0x672a, 0x7533, 0x9149, 0x620c, 0x4ea5) # 12
	CHINESE_GAPJA_UNIT: Final[tuple[int, ...]] = (0x5e74, 0x6708, 0x65e5) # 3 年, 月, 日: year, month day in chinese

	INTERCALATION_STR: Final[tuple[int, ...]] = (0xc724, 0x958f) # 2 ('윤', '閏'): Leap, resp. in korean, and in chinese

	# 8 figure hexadecimal -> 32bits; len: 1051;
	KOREAN_LUNAR_DATA: Final[tuple[int, ...]] = (
			0x82c60a57, 0x82fec52b, 0x82c40d2a, 0x82c60d55, 0xc30095ad, 0x82c4056a, 0x82c6096d, 0x830054dd, 0xc2c404ad, 0x82c40a4d,
			0x83002e4d, 0x82c40b26, 0xc300ab56, 0x82c60ad5, 0x82c4035a, 0x8300697a, 0xc2c6095b, 0x82c4049b, 0x83004a9b, 0x82c40a4b,
			0xc301caa5, 0x82c406aa, 0x82c60ad5, 0x830092dd, 0xc2c402b5, 0x82c60957, 0x82fe54ae, 0x82c60c97, 0xc2c4064b, 0x82ff254a,
			0x82c60da9, 0x8300a6b6, 0xc2c6066d, 0x82c4026e, 0x8301692e, 0x82c4092e, 0xc2c40c96, 0x83004d95, 0x82c40d4a, 0x8300cd69,
			0xc2c40b58, 0x82c80d6b, 0x8301926b, 0x82c4025d, 0xc2c4092b, 0x83005aab, 0x82c40a95, 0x82c40b4a, 0xc3021eab, 0x82c402d5,
			0x8301b55a, 0x82c604bb, 0xc2c4025b, 0x83007537, 0x82c4052b, 0x82c40695, 0xc3003755, 0x82c406aa, 0x8303cab5, 0x82c40275,
			0xc2c404b6, 0x83008a5e, 0x82c40a56, 0x82c40d26, 0xc3005ea6, 0x82c60d55, 0x82c405aa, 0x83001d6a, 0xc2c6096d, 0x8300b4af,
			0x82c4049d, 0x82c40a4d, 0xc3007d2d, 0x82c40aa6, 0x82c60b55, 0x830045d5, 0xc2c4035a, 0x82c6095d, 0x83011173, 0x82c4045b,
			0xc3009a4f, 0x82c4064b, 0x82c40aa5, 0x83006b69, 0xc2c606b5, 0x82c402da, 0x83002ab6, 0x82c60937, 0xc2fec497, 0x82c60c97,
			0x82c4064b, 0x82fe86aa, 0xc2c60da5, 0x82c405b4, 0x83034a6d, 0x82c402ae, 0xc2c40e61, 0x83002d2e, 0x82c40c96, 0x83009d4d,
			0x82c40d4a, 0x82c60d65, 0x83016595, 0x82c6055d, 0xc2c4026d, 0x83002a5d, 0x82c4092b, 0x8300aa97, 0xc2c40a95, 0x82c40b4a,
			0x83008b5a, 0x82c60ad5, 0xc2c6055b, 0x830042b7, 0x82c40457, 0x82c4052b, 0xc3001d2b, 0x82c40695, 0x8300972d, 0x82c405aa,
			0xc2c60ab5, 0x830054ed, 0x82c404b6, 0x82c60a57, 0xc2ff344e, 0x82c40d26, 0x8301be92, 0x82c60d55, 0xc2c405aa, 0x830089ba,
			0x82c6096d, 0x82c404ae, 0xc3004a9d, 0x82c40a4d, 0x82c40d25, 0x83002f25, 0xc2c40b54, 0x8303ad69, 0x82c402da, 0x82c6095d,
			0xc301649b, 0x82c4049b, 0x82c40a4b, 0x83004b4b, 0xc2c406a5, 0x8300bb53, 0x82c406b4, 0x82c60ab6, 0xc3018956, 0x82c60997,
			0x82c40497, 0x83004697, 0xc2c4054b, 0x82fec6a5, 0x82c60da5, 0x82c405ac, 0xc303aab5, 0x82c4026e, 0x82c4092e, 0x83006cae,
			0xc2c40c96, 0x82c40d4a, 0x83002f4a, 0x82c60d55, 0xc300b56b, 0x82c6055b, 0x82c4025d, 0x8300793d, 0xc2c40927, 0x82c40a95,
			0x83015d15, 0x82c40b4a, 0xc2c60b55, 0x830112d5, 0x82c604db, 0x82fe925e, 0xc2c60a57, 0x82c4052b, 0x83006aab, 0x82c40695,
			0xc2c406aa, 0x83003baa, 0x82c60ab5, 0x8300b4b7, 0xc2c404ae, 0x82c60a57, 0x82fe752e, 0x82c40d26, 0xc2c60e93, 0x830056d5,
			0x82c405aa, 0x82c609b5, 0xc300256d, 0x82c404ae, 0x8301aa4d, 0x82c40a4d, 0xc2c40d26, 0x83006d65, 0x82c40b52, 0x82c60d6a,
			0xc30026da, 0x82c6095d, 0x8301c49d, 0x82c4049b, 0xc2c40a4b, 0x83008aab, 0x82c406a5, 0x82c40b54, 0xc3004bb4, 0x82c60ab6,
			0x82c6095b, 0x83002537, 0xc2c40497, 0x8300964f, 0x82c4054b, 0x82c406a5, 0xc30176c5, 0x82c405ac, 0x82c60ab6, 0x8301386e,
			0xc2c4092e, 0x8300cc97, 0x82c40c96, 0x82c40d4a, 0xc3008daa, 0x82c60b55, 0x82c4056a, 0x83025adb, 0xc2c4025d, 0x82c4092e,
			0x83002d2b, 0x82c40a95, 0xc3009d4d, 0x82c40b2a, 0x82c60b55, 0x83007575, 0xc2c404da, 0x82c60a5b, 0x83004557, 0x82c4052b,
			0xc301ca93, 0x82c40693, 0x82c406aa, 0x83008ada, 0xc2c60ae5, 0x82c404b6, 0x83004aae, 0x82c60a57, 0xc2c40527, 0x82ff2526,
			0x82c60e53, 0x8300a6cb, 0xc2c405aa, 0x82c605ad, 0x830164ad, 0x82c404ae, 0xc2c40a4e, 0x83004d4d, 0x82c40d26, 0x8300bd53,
			0xc2c40b52, 0x82c60b6a, 0x8301956a, 0x82c60557, 0xc2c4049d, 0x83015a1b, 0x82c40a4b, 0x82c40aa5, 0xc3001ea5, 0x82c40b52,
			0x8300bb5a, 0x82c60ab6, 0xc2c6095b, 0x830064b7, 0x82c40497, 0x82c4064b, 0xc300374b, 0x82c406a5, 0x8300b6b3, 0x82c405ac,
			0xc2c60ab6, 0x830182ad, 0x82c4049e, 0x82c40a4d, 0xc3005d4b, 0x82c40b25, 0x82c40b52, 0x83012e52, 0xc2c60b5a, 0x8300a95e,
			0x82c6095b, 0x82c4049b, 0xc3006a57, 0x82c40a4b, 0x82c40aa5, 0x83004ba5, 0xc2c406d4, 0x8300cad6, 0x82c60ab6, 0x82c60937,
			0x8300849f, 0x82c40497, 0x82c4064b, 0x82fe56ca, 0xc2c60da5, 0x82c405aa, 0x83001d6c, 0x82c60a6e, 0xc300b92f, 0x82c4092e,
			0x82c40c96, 0x83007d55, 0xc2c40d4a, 0x82c60d55, 0x83013555, 0x82c4056a, 0xc2c60a6d, 0x83001a5d, 0x82c4092b, 0x83008a5b,
			0xc2c40a95, 0x82c40b2a, 0x83015b2a, 0x82c60ad5, 0xc2c404da, 0x83001cba, 0x82c60a57, 0x8300952f, 0xc2c40527, 0x82c40693,
			0x830076b3, 0x82c406aa, 0xc2c60ab5, 0x83003575, 0x82c404b6, 0x8300ca67, 0xc2c40a2e, 0x82c40d16, 0x83008e96, 0x82c40d4a,
			0xc2c60daa, 0x830055ea, 0x82c6056d, 0x82c404ae, 0xc301285d, 0x82c40a2d, 0x8300ad17, 0x82c40aa5, 0xc2c40b52, 0x83007d74,
			0x82c60ada, 0x82c6055d, 0xc300353b, 0x82c4045b, 0x82c40a2b, 0x83011a2b, 0xc2c40aa5, 0x83009b55, 0x82c406b2, 0x82c60ad6,
			0xc3015536, 0x82c60937, 0x82c40457, 0x83003a57, 0xc2c4052b, 0x82feaaa6, 0x82c60d95, 0x82c405aa, 0xc3017aac, 0x82c60a6e,
			0x82c4052e, 0x83003cae, 0xc2c40a56, 0x8300bd2b, 0x82c40d2a, 0x82c60d55, 0xc30095ad, 0x82c4056a, 0x82c60a6d, 0x8300555d,
			0xc2c4052b, 0x82c40a8d, 0x83002e55, 0x82c40b2a, 0xc300ab56, 0x82c60ad5, 0x82c404da, 0x83006a7a, 0xc2c60a57, 0x82c4051b,
			0x83014a17, 0x82c40653, 0xc301c6a9, 0x82c405aa, 0x82c60ab5, 0x830092bd, 0xc2c402b6, 0x82c60a37, 0x82fe552e, 0x82c40d16,
			0x82c60e4b, 0x82fe3752, 0x82c60daa, 0x8301b5b4, 0xc2c6056d, 0x82c402ae, 0x83007a3d, 0x82c40a2d, 0xc2c40d15, 0x83004d95,
			0x82c40b52, 0x8300cb69, 0xc2c60ada, 0x82c6055d, 0x8301925b, 0x82c4045b, 0xc2c40a2b, 0x83005aab, 0x82c40a95, 0x82c40b52,
			0xc3001eaa, 0x82c60ab6, 0x8300c55b, 0x82c604b7, 0xc2c40457, 0x83007537, 0x82c4052b, 0x82c40695, 0xc3014695, 0x82c405aa,
			0x8300cab5, 0x82c60a6e, 0xc2c404ae, 0x83008a5e, 0x82c40a56, 0x82c40d2a, 0xc3006eaa, 0x82c60d55, 0x82c4056a, 0x8301295a,
			0xc2c6095d, 0x8300b4af, 0x82c4049b, 0x82c40a4d, 0xc3007d2d, 0x82c40b2a, 0x82c60b55, 0x830045d5, 0xc2c402da, 0x82c6095b,
			0x83011157, 0x82c4049b, 0xc3009a4f, 0x82c4064b, 0x82c406a9, 0x83006aea, 0xc2c606b5, 0x82c402b6, 0x83002aae, 0x82c60937,
			0xc2ffb496, 0x82c40c96, 0x82c60e4b, 0x82fe76b2, 0xc2c60daa, 0x82c605ad, 0x8300336d, 0x82c4026e, 0xc2c4092e, 0x83002d2d,
			0x82c40c95, 0x83009d4d, 0xc2c40b4a, 0x82c60b69, 0x8301655a, 0x82c6055b, 0xc2c4025d, 0x83002a5b, 0x82c4092b, 0x8300aa97,
			0xc2c40695, 0x82c4074a, 0x83008b5a, 0x82c60ab6, 0xc2c6053b, 0x830042b7, 0x82c40257, 0x82c4052b, 0xc3001d2b, 0x82c40695,
			0x830096ad, 0x82c405aa, 0xc2c60ab5, 0x830054ed, 0x82c404ae, 0x82c60a57, 0xc2ff344e, 0x82c40d2a, 0x8301bd94, 0x82c60b55,
			0x82c4056a, 0x8300797a, 0x82c6095d, 0x82c404ae, 0xc3004a9b, 0x82c40a4d, 0x82c40d25, 0x83011aaa, 0xc2c60b55, 0x8300956d,
			0x82c402da, 0x82c6095b, 0xc30054b7, 0x82c40497, 0x82c40a4b, 0x83004b4b, 0xc2c406a9, 0x8300cad5, 0x82c605b5, 0x82c402b6,
			0xc300895e, 0x82c6092f, 0x82c40497, 0x82fe4696, 0xc2c40d4a, 0x8300cea5, 0x82c60d69, 0x82c6056d, 0xc301a2b5, 0x82c4026e,
			0x82c4092e, 0x83006cad, 0xc2c40c95, 0x82c40d4a, 0x83002f4a, 0x82c60b59, 0xc300c56d, 0x82c6055b, 0x82c4025d, 0x8300793b,
			0xc2c4092b, 0x82c40a95, 0x83015b15, 0x82c406ca, 0xc2c60ad5, 0x830112b6, 0x82c604bb, 0x8300925f, 0xc2c40257, 0x82c4052b,
			0x82fe6aaa, 0x82c60e95, 0xc2c406aa, 0x83003baa, 0x82c60ab5, 0x8300b4b7, 0xc2c404ae, 0x82c60a57, 0x82fe752d, 0x82c40d26,
			0xc2c60d95, 0x830055d5, 0x82c4056a, 0x82c6096d, 0xc300255d, 0x82c404ae, 0x8300aa4f, 0x82c40a4d, 0xc2c40d25, 0x83006d69,
			0x82c60b55, 0x82c4035a, 0xc3002aba, 0x82c6095b, 0x8301c49b, 0x82c40497, 0xc2c40a4b, 0x83008b2b, 0x82c406a5, 0x82c406d4,
			0xc3034ab5, 0x82c402b6, 0x82c60937, 0x8300252f, 0xc2c40497, 0x82fe964e, 0x82c40d4a, 0x82c60ea5, 0xc30166a9, 0x82c6056d,
			0x82c402b6, 0x8301385e, 0xc2c4092e, 0x8300bc97, 0x82c40a95, 0x82c40d4a, 0xc3008daa, 0x82c60b4d, 0x82c6056b, 0x830042db,
			0xc2c4025d, 0x82c4092d, 0x83002d2b, 0x82c40a95, 0xc3009b4d, 0x82c406aa, 0x82c60ad5, 0x83006575, 0xc2c604bb, 0x82c4025b,
			0x83013457, 0x82c4052b, 0xc2ffba94, 0x82c60e95, 0x82c406aa, 0x83008ada, 0xc2c609b5, 0x82c404b6, 0x83004aae, 0x82c60a4f,
			0xc2c20526, 0x83012d26, 0x82c60d55, 0x8301a5a9, 0xc2c4056a, 0x82c6096d, 0x8301649d, 0x82c4049e, 0xc2c40a4d, 0x83004d4d,
			0x82c40d25, 0x8300bd53, 0xc2c40b54, 0x82c60b5a, 0x8301895a, 0x82c6095b, 0xc2c4049b, 0x83004a97, 0x82c40a4b, 0x82c40aa5,
			0xc3001ea5, 0x82c406d4, 0x8302badb, 0x82c402b6, 0xc2c60937, 0x830064af, 0x82c40497, 0x82c4064b, 0xc2fe374a, 0x82c60da5,
			0x8300b6b5, 0x82c6056d, 0xc2c402ae, 0x8300793e, 0x82c4092e, 0x82c40c96, 0xc3015d15, 0x82c40d4a, 0x82c60da5, 0x83013555,
			0xc2c4056a, 0x83007a7a, 0x82c60a5d, 0x82c4092d, 0xc3006aab, 0x82c40a95, 0x82c40b4a, 0x83004baa, 0xc2c60ad5, 0x82c4055a,
			0x830128ba, 0x82c60a5b, 0xc3007537, 0x82c4052b, 0x82c40693, 0x83015715, 0xc2c406aa, 0x82c60ad5, 0x830035b5, 0x82c404b6,
			0xc3008a5e, 0x82c40a4e, 0x82c40d26, 0x83006ea6, 0xc2c40d52, 0x82c60daa, 0x8301466a, 0x82c6056d, 0xc2c404ae, 0x83003a9d,
			0x82c40a4d, 0x83007d2b, 0xc2c40b25, 0x82c40d52, 0x83015d54, 0x82c60b5a, 0xc2c6055d, 0x8300355b, 0x82c4049b, 0x83007657,
			0x82c40a4b, 0x82c40aa5, 0x83006b65, 0x82c406d2, 0xc2c60ada, 0x830045b6, 0x82c60937, 0x82c40497, 0xc3003697, 0x82c4064d,
			0x82fe76aa, 0x82c60da5, 0xc2c405aa, 0x83005aec, 0x82c60aae, 0x82c4092e, 0xc3003d2e, 0x82c40c96, 0x83018d45, 0x82c40d4a,
			0xc2c60d55, 0x83016595, 0x82c4056a, 0x82c60a6d, 0xc300455d, 0x82c4052d, 0x82c40a95, 0x83013c95, 0xc2c40b4a, 0x83017b4a,
			0x82c60ad5, 0x82c4055a, 0xc3015a3a, 0x82c60a5b, 0x82c4052b, 0x83014a17, 0xc2c40693, 0x830096ab, 0x82c406aa, 0x82c60ab5,
			0xc30064f5, 0x82c404b6, 0x82c60a57, 0x82fe452e, 0xc2c40d16, 0x82c60e93, 0x82fe3752, 0x82c60daa, 0xc30175aa, 0x82c6056d,
			0x82c404ae, 0x83015a1d, 0xc2c40a2d, 0x82c40d15, 0x83004da5, 0x82c40b52, 0xc3009d6a, 0x82c60ada, 0x82c6055d, 0x8301629b,
			0xc2c4045b, 0x82c40a2b, 0x83005b2b, 0x82c40a95, 0xc2c40b52, 0x83012ab2, 0x82c60ad6, 0x83017556, 0xc2c60537, 0x82c40457,
			0x83005657, 0x82c4052b, 0xc2c40695, 0x83003795, 0x82c405aa, 0x8300aab6, 0xc2c60a6d, 0x82c404ae, 0x83006a6e, 0x82c40a56,
			0xc2c40d2a, 0x83005eaa, 0x82c60d55, 0x82c405aa, 0xc3003b6a, 0x82c60a6d, 0x830074bd, 0x82c404ab, 0xc2c40a8d, 0x83005d55,
			0x82c40b2a, 0x82c60b55, 0xc30045d5, 0x82c404da, 0x82c6095d, 0x83002557, 0xc2c4049b, 0x83006a97, 0x82c4064b, 0x82c406a9,
			0x83004baa, 0x82c606b5, 0x82c402ba, 0x83002ab6, 0xc2c60937, 0x82fe652e, 0x82c40d16, 0x82c60e4b, 0xc2fe56d2, 0x82c60da9,
			0x82c605b5, 0x8300336d, 0xc2c402ae, 0x82c40a2e, 0x83002e2d, 0x82c40c95, 0xc3006d55, 0x82c40b52, 0x82c60b69, 0x830045da,
			0xc2c6055d, 0x82c4025d, 0x83003a5b, 0x82c40a2b, 0xc3017a8b, 0x82c40a95, 0x82c40b4a, 0x83015b2a, 0xc2c60ad5, 0x82c6055b,
			0x830042b7, 0x82c40257, 0xc300952f, 0x82c4052b, 0x82c40695, 0x830066d5, 0xc2c405aa, 0x82c60ab5, 0x8300456d, 0x82c404ae,
			0xc2c60a57, 0x82ff3456, 0x82c40d2a, 0x83017e8a, 0xc2c60d55, 0x82c405aa, 0x83005ada, 0x82c6095d, 0xc2c404ae, 0x83004aab,
			0x82c40a4d, 0x83008d2b, 0xc2c40b29, 0x82c60b55, 0x83007575, 0x82c402da, 0xc2c6095d, 0x830054d7, 0x82c4049b, 0x82c40a4b,
			0xc3013a4b, 0x82c406a9, 0x83008ad9, 0x82c606b5, 0xc2c402b6, 0x83015936, 0x82c60937, 0x82c40497, 0xc2fe4696, 0x82c40e4a,
			0x8300aea6, 0x82c60da9, 0xc2c605ad, 0x830162ad, 0x82c402ae, 0x82c4092e, 0xc3005cad, 0x82c40c95, 0x82c40d4a, 0x83013d4a,
			0xc2c60b69, 0x8300757a, 0x82c6055b, 0x82c4025d, 0xc300595b, 0x82c4092b, 0x82c40a95, 0x83004d95, 0xc2c40b4a, 0x82c60b55,
			0x830026d5, 0x82c6055b, 0xc3006277, 0x82c40257, 0x82c4052b, 0x82fe5aaa, 0xc2c60e95, 0x82c406aa, 0x83003baa, 0x82c60ab5,
			0x830084bd, 0x82c404ae, 0x82c60a57, 0x82fe554d, 0xc2c40d26, 0x82c60d95, 0x83014655, 0x82c4056a, 0xc2c609ad, 0x8300255d,
			0x82c404ae, 0x83006a5b, 0xc2c40a4d, 0x82c40d25, 0x83005da9, 0x82c60b55, 0xc2c4056a, 0x83002ada, 0x82c6095d, 0x830074bb,
			0xc2c4049b, 0x82c40a4b, 0x83005b4b, 0x82c406a9, 0xc2c40ad4, 0x83024bb5, 0x82c402b6, 0x82c6095b, 0xc3002537, 0x82c40497,
			0x82fe6656, 0x82c40e4a, 0xc2c60ea5, 0x830156a9, 0x82c605b5, 0x82c402b6, 0xc30138ae, 0x82c4092e, 0x83017c8d, 0x82c40c95,
			0xc2c40d4a, 0x83016d8a, 0x82c60b69, 0x82c6056d, 0xc301425b, 0x82c4025d, 0x82c4092d, 0x83002d2b, 0xc2c40a95, 0x83007d55,
			0x82c40b4a, 0x82c60b55, 0xc3015555, 0x82c604db, 0x82c4025b, 0x83013857, 0xc2c4052b, 0x83008a9b, 0x82c40695, 0x82c406aa,
			0xc3006aea, 0x82c60ab5, 0x82c404b6, 0x83004aae, 0xc2c60a57, 0x82c40527, 0x82fe3726, 0x82c60d95, 0xc30076b5, 0x82c4056a,
			0x82c609ad, 0x830054dd, 0xc2c404ae, 0x82c40a4e, 0x83004d4d, 0x82c40d25, 0xc3008d59, 0x82c40b54, 0x82c60d6a, 0x8301695a,
			0xc2c6095b, 0x82c4049b, 0x83004a9b, 0x82c40a4b, 0xc300ab27, 0x82c406a5, 0x82c406d4, 0x83026b75, 0xc2c402b6, 0x82c6095b,
			0x830054b7, 0x82c40497, 0xc2c4064b, 0x82fe374a, 0x82c60ea5, 0x830086d9, 0xc2c605ad, 0x82c402b6, 0x8300596e, 0x82c4092e,
			0xc2c40c96, 0x83004e95, 0x82c40d4a, 0x82c60da5, 0xc3002755, 0x82c4056c, 0x83027abb, 0x82c4025d, 0xc2c4092d, 0x83005cab,
			0x82c40a95, 0x82c40b4a, 0xc3013b4a, 0x82c60b55, 0x8300955d, 0x82c404ba, 0xc2c60a5b, 0x83005557, 0x82c4052b, 0x82c40a95,
			0xc3004b95, 0x82c406aa, 0x82c60ad5, 0x830026b5, 0xc2c404b6, 0x83006a6e, 0x82c60a57, 0x82c40527, 0xc2fe56a6, 0x82c60d93,
			0x82c405aa, 0x83003b6a, 0xc2c6096d, 0x8300b4af, 0x82c404ae, 0x82c40a4d, 0xc3016d0d, 0x82c40d25, 0x82c40d52, 0x83005dd4,
			0xc2c60b6a, 0x82c6096d, 0x8300255b, 0x82c4049b, 0xc3007a57, 0x82c40a4b, 0x82c40b25, 0x83015b25, 0xc2c406d4, 0x82c60ada,
			0x830138b6)

	def __init__(self) -> None:
		self.lunar_year:int = 0
		self.lunar_month:int = 1
		self.lunar_day:int = 1
		self.is_intercalation:bool = False

		self.solar_year:int = 0
		self.solar_month:int = 1
		self.solar_day:int = 1

		# [Cheongan, Ganji, Unit]
		self.__gapjaYearInx:list[int] = [0, 0, 0]
		self.__gapjaMonthInx:list[int] = [0, 0, 1]
		self.__gapjaDayInx:list[int] = [0, 0, 2]

	def lunar_iso_format(self) -> str:
		"""Get lunar date as a string in iso format `'YYYY-MM-DD'` with optional trailing argument `'YYYY-MM-DD Intercalation'` if `self.isIntercalation`.

		Returns:
			str: Lunar date in iso format `'YYYY-MM-DD'` with optional trailing argument `'YYYY-MM-DD Intercalation'` if `self.isIntercalation`
		"""
		date_str:str = "%04d-%02d-%02d" % (self.lunar_year, self.lunar_month, self.lunar_day)
		if self.is_intercalation :
			date_str += " Intercalation"
		return date_str

	def solar_iso_format(self) -> str:
		"""Get solar date as a string in iso format `'YYYY-MM-DD'`.

		Returns:
			str: Solar date in iso format `'YYYY-MM-DD'`
		"""
		return "%04d-%02d-%02d" % (self.solar_year, self.solar_month, self.solar_day)

	def __get_lunar_data(self, year:int) -> int:
		"""Fetch `year-self.KOREAN_LUNAR_BASE_YEAR` (`year-1000`)  element in `self.KOREAN_LUNAR_DATA`.

		Args:
			year (int): year

		Returns:
			int: lunar data
		"""
		return self.KOREAN_LUNAR_DATA[year - self.KOREAN_LUNAR_BASE_YEAR]

	def __get_lunar_intercalation_month(self, lunar_data:int) -> int:
		"""Get lunar intercalation month from lunar data.

		Binary right-shift lunar data by 12 bits and mask to get the last 4 bits:
		`|0000|0000|0000|0000|XXXX|....|....|....|`

		Args:
			lunar_data (int): lunar data

		Returns:
			int: lunar intercalation month
		"""
		return (lunar_data >> 12) & 0x000F

	def __get_lunar_days_(self, lunar_data:int, month:int|None=None, is_intercalation:bool|None=None) -> int:
		"""Get number of days in a given **lunar_data** year or month of the year.

		If **month** is given with **is_intercalation**:
		* If **is_intercalation** & the **month** is an intercalation month (here, a month where an intercalation month while be appended) for the given year:
			Reads `|0000|0000|0000|000X|....|....|....|....|` from lunar data which indicates (`X` bit) if the intercalation month lasts 30 days (or 29 if `False`)
		* Else:
			Reads `|0000|0000|0000|0000|0000|YYYY|YYYY|YYYY|` from lunar data where: For each regular month (from 1(leftmost `Y` bit) to 12(rightmost `Y` bit)), indicates if it lasts 30 days (or 29 if `False`)
		
		Else:

		Reads `|0000|00XX|XXXX|XXX.|....|....|....|....|` from lunar data which indicates the year duration in days (on 9 bits, for a max of up to 511 days)

		> Note: On the month of intercalation, first the month happens, then the intercalation month happens before the next month begins.

		Args:
			lunar_data (int): Lunar data of a year
			month (int | None, optional): Month, if given. Defaults to None.
			is_intercalation (bool | None, optional): Get intercalation month duration. Defaults to None.

		Returns:
			int: Duration in days
		"""
		if month is not None and is_intercalation is not None :
			if is_intercalation and (self.__get_lunar_intercalation_month(lunar_data) == month):
				# `|0000|0000|0000|000X|....|....|....|....|`
				days = self.LUNAR_BIG_MONTH_DAY if ((lunar_data >>16) & 0x01) > 0 else self.LUNAR_SMALL_MONTH_DAY
			else:
				# `|0000|0000|0000|0000|0000|YYYY|YYYY|YYYY|`: one of the Ys
				days = self.LUNAR_BIG_MONTH_DAY if ((lunar_data >> (12 - month)) & 0x01) > 0 else self.LUNAR_SMALL_MONTH_DAY
		else:
			# `|0000|00XX|XXXX|XXX.|....|....|....|....|`: up to 511 days
			days = (lunar_data >> 17) & 0x01FF
		return days


	def __get_lunar_days(self, year:int, month:int|None=None, is_intercalation:bool|None=None) -> int:
		"""Get number of days in a given lunar year or month of the year.

		Simply a wrapper for method **__get_lunar_days_** after getting the lunar data for the given **year**.

		Args:
			year (int): Year
			month (int | None, optional): Month, if given. Defaults to None.
			is_intercalation (bool | None, optional): Takes intercalation into account. Defaults to None.

		Returns:
			int: Duration in days
		"""
		lunar_data:int = self.__get_lunar_data(year)
		days:int = self.__get_lunar_days_(lunar_data, month, is_intercalation)
		
		return days

	def __get_lunar_days_before_base_year(self, year:int) -> int:
		"""Get duration in days from korean lunar base year to given **year**.

		Args:
			year (int): Year

		Returns:
			int: Duration in days
		"""
		days:int = 0
		for base_year in range(self.KOREAN_LUNAR_BASE_YEAR, year+1):
			days += self.__get_lunar_days(base_year)
		return days

	def __get_lunar_days_before_base_month(self, year:int, month:int, is_intercalation:bool) -> int:
		"""Get number of lunar days from the first day of the year to the end of the given **month** for the given **year**.

		If **year**<1000 or 13<=**month**<=0: Returns 0

		Args:
			year (int): Year
			month (int): Month
			is_intercalation (bool): Consider intercalation (ignored if `False`)

		Returns:
			int: Duration in days
		"""
		days:int = 0
		if (year >= self.KOREAN_LUNAR_BASE_YEAR) and (13 > month > 0):
			for base_month in range(1, month+1):
				days += self.__get_lunar_days(year, base_month, False)

			if is_intercalation:
				intercalation_month = self.__get_lunar_intercalation_month(self.__get_lunar_data(year))
				if (intercalation_month > 0) and intercalation_month < month+1:
					days += self.__get_lunar_days(year, intercalation_month, True)
		return days

	def __get_lunar_abs_days(self, year:int, month:int, day:int, is_intercalation:bool) -> int:
		"""Get duration in days between lunar base year and given lunar date.

		Args:
			year (int): Year (lunar)
			month (int): Month (lunar)
			day (int): Day (lunar)
			is_intercalation (bool): Indicates if it is the regular or the lunar intercalation month (only affects **month** if it has an intercalation month)

		Returns:
			int: Duration in days
		"""
		days:int = self.__get_lunar_days_before_base_year(year-1) + self.__get_lunar_days_before_base_month(year, month-1, True) + day
		if is_intercalation and (self.__get_lunar_intercalation_month(self.__get_lunar_data(year)) == month):
			# If the day is in the intercalation month, then we have to add the duration of the regular month which already happened before the intercalation.
			days += self.__get_lunar_days(year, month, False)
		return days

	def __is_solar_intercalation_year(self, lunar_data:int) -> bool:
		"""Indicate if the lunar year is a solar intercalation year, i.e. it has an intercalation day (Feb. duration: 29 days instead of 28 days).

		Right-shift by 30 bits, and mask to get the last bit:

		`|0X..|....|....|....|....|....|....|....|`

		Then interpret the `X` bit as a `bool` value.

		Args:
			lunar_data (int): Lunar data

		Returns:
			bool: `True` if year of lunar data is a solar intercalation year, else `False`
		"""
		# `|0X..|....|....|....|....|....|....|....|`
		return ((lunar_data >> 30) & 0x01) > 0

	def __get_solar_days_(self, lunar_data:int, month:int|None=None) -> int:
		"""Get duration of solar month for **month**, if given, else of solar year for which **lunar_data** was provided.

		> Note: Solar intercalation indicates if Feb. is short or long for that year. It is extracted from **lunar_data** and taken into account for the returned duration.

		Args:
			lunar_data (int): Lunar data
			month (int | None, optional): Month. Defaults to None.

		Returns:
			int: Duration in days
		"""
		if month is not None:
			days = self.SOLAR_DAYS[12] if (month == 2) and self.__is_solar_intercalation_year(lunar_data) else self.SOLAR_DAYS[month - 1]
		else:
			days = self.SOLAR_BIG_YEAR_DAY if self.__is_solar_intercalation_year(lunar_data) else self.SOLAR_SMALL_YEAR_DAY
		return days


	def __get_solar_days(self, year:int, month:int|None=None) -> int:
		"""Get duration of solar month for given **month** of given year **year**, if given, else only of given solar year.

		Simply a wrapper for method **__get_solar_days_** after getting the lunar data for the given **year**.

		Args:
			year (int): Year
			month (int | None, optional): Month. Defaults to None.

		Returns:
			int: Duration in days
		"""
		lunar_data:int = self.__get_lunar_data(year)
		days:int = self.__get_solar_days_(lunar_data, month)
		return days

	def __get_solar_days_before_base_year(self, year:int) -> int:
		"""Get duration, in days, between the begining of the base year (1000) and the end of the given year **year**.

		Args:
			year (int): Year

		Returns:
			int: Duration in days
		"""
		days:int = 0
		for base_year in range(self.KOREAN_LUNAR_BASE_YEAR, year+1):
			days += self.__get_solar_days(base_year)
		return days

	def __get_solar_days_before_base_month(self, year:int, month:int) -> int:
		"""Get duration, in days, between the begining of the year and the end of the given month for year **year**.

		Args:
			year (int): Year
			month (int): Month

		Returns:
			int: Duration in days
		"""
		days:int = 0
		for base_month in range(1, month+1):
			days += self.__get_solar_days(year, base_month)
		return days

	def __get_solar_abs_days(self, year:int, month:int, day:int) -> int:
		"""Get duration in days between base lunar date (from `self.KOREAN_LUNAR_MIN_VALUE`: 1000/01/01) - or equivalently, base solar date (from `self.KOREAN_SOLAR_MIN_VALUE`: 1000/02/13) -, and the given solar date (included).

		Basically, get the duration in days from the beginning of the base solar year (1000) to the given solar date. Then, substract the `self.SOLAR_LUNAR_DAY_DIFF`: 43 days, to get the difference to the beginning of the base lunar year.

		Args:
			year (int): Year
			month (int): Month
			day (int): Day

		Returns:
			int: Duration in days
		"""
		days:int = self.__get_solar_days_before_base_year(year-1) + self.__get_solar_days_before_base_month(year, month-1) + day
		days -= self.SOLAR_LUNAR_DAY_DIFF
		return days

	def __set_solar_date_by_lunar_date(self, lunar_year:int, lunar_month:int, lunar_day:int, is_intercalation:bool) -> None:
		"""Set solar date class instance properties to given lunar date converted in solar date.
		
		Args:
			lunar_year (int): Year
			lunar_month (int): Month
			lunar_day (int): Day
			is_intercalation (bool): Whether the day is in the regular or intercalation month (only applied if **lunar_month** has an intercalation month)
		"""
		abs_days = self.__get_lunar_abs_days(lunar_year, lunar_month, lunar_day, is_intercalation)
		solar_year:int = 0
		solar_month:int = 0
		solar_day:int = 0

		solar_year = lunar_year if (abs_days < self.__get_solar_abs_days(lunar_year+1, 1, 1)) else lunar_year+1

		for month in range(12, 0, -1) :
			abs_days_by_month:int = self.__get_solar_abs_days(solar_year, month, 1)
			if (abs_days >= abs_days_by_month) :
				solar_month = month
				solar_day = abs_days - abs_days_by_month +1
				break

		self.solar_year = solar_year
		self.solar_month = solar_month
		self.solar_day  = solar_day

	def __set_lunar_date_by_solar_date(self, solar_year:int, solar_month:int, solar_day:int) -> None:
		"""Set solar date class instance properties to given solar date converted in lunar date.

		Args:
			solar_year (int): Year
			solar_month (int): Month
			solar_day (int): Day
		"""
		abs_days:int = self.__get_solar_abs_days(solar_year, solar_month, solar_day)
		lunar_year:int = solar_year if (abs_days >= self.__get_lunar_abs_days(solar_year, 1, 1, False)) else solar_year-1
		lunar_month:int = 0
		lunar_day:int = 0
		is_intercalation:bool = False
		
		for month in range(12, 0, -1) :
			abs_days_by_month = self.__get_lunar_abs_days(lunar_year, month, 1, False)
			if abs_days >= abs_days_by_month:
				lunar_month = month
				if self.__get_lunar_intercalation_month(self.__get_lunar_data(lunar_year)) == month :
					is_intercalation = abs_days >= self.__get_lunar_abs_days(lunar_year, month, 1, True)
				
				lunar_day = abs_days - self.__get_lunar_abs_days(lunar_year, lunar_month, 1, is_intercalation) + 1
				break

		self.lunar_year = lunar_year
		self.lunar_month = lunar_month
		self.lunar_day = lunar_day        
		self.is_intercalation = is_intercalation

	def __check_valid_date(self, is_lunar:bool, is_intercalation:bool, year:int, month:int, day:int) -> bool:
		"""Check if the given date is valid.

		Args:
			is_lunar (bool): Lunar or solar date
			is_intercalation (bool): Intercalation (has to exist if lunar date) or regular month
			year (int): Year
			month (int): Month
			day (int): Day

		Returns:
			bool: Indicates if given date is valid
		"""
		is_valid:bool = False
		date_value:int = year*10000 + month*100 + day
		#1582. 10. 5 ~ 1582. 10. 14 is not valid when strictly considering Julian/Gregorian: But is valid in Gregorian Proleptic
		min_value:int = self.KOREAN_LUNAR_MIN_VALUE if is_lunar else self.KOREAN_SOLAR_MIN_VALUE
		max_value:int = self.KOREAN_LUNAR_MAX_VALUE if is_lunar else self.KOREAN_SOLAR_MAX_VALUE

		if min_value <= date_value and max_value >= date_value : # noqa: SIM102
			if month > 0 and month < 13 and day > 0 :
				day_limit = self.__get_lunar_days(year, month, is_intercalation) if is_lunar else self.__get_solar_days(year, month)
				# if not is_lunar and year == 1582 and month == 10 :
				# 	if day > 4 and day < 15 :
				# 		return is_valid
				# 	else:
				# 		day_limit += 10

				if day <= day_limit :
					is_valid = True
				
				# Check whether intercalation is correct for lunar date
				if is_lunar and is_intercalation and self.__get_lunar_intercalation_month(self.__get_lunar_data(year)) != month:
					is_valid = False

		return is_valid

	def set_lunar_date(self, lunar_year:int, lunar_month:int, lunar_day:int, is_intercalation:bool) -> bool:
		"""Check if given lunar date is valid & subsequently set the internal dates (lunar & solar) to the one given, if it is valid.

		Args:
			lunar_year (int): Year
			lunar_month (int): month
			lunar_day (int): Day
			is_intercalation (bool): Intercalation (has to exist) or regular month 

		Returns:
			bool: Indicates if given lunar date is valid
		"""
		is_valid:bool = False
		if self.__check_valid_date(True, is_intercalation, lunar_year, lunar_month, lunar_day):
			self.lunar_year = lunar_year
			self.lunar_month = lunar_month
			self.lunar_day = lunar_day
			# Check pushed to __check_valid_date
			# self.is_intercalation = is_intercalation and (self.__get_lunar_intercalation_month(self.__get_lunar_data(lunar_year)) == lunar_month)
			self.is_intercalation = is_intercalation
			self.__set_solar_date_by_lunar_date(lunar_year, lunar_month, lunar_day, is_intercalation)
			is_valid = True
		return is_valid

	def set_solar_date(self, solar_year:int, solar_month:int, solar_day:int) -> bool:
		"""Check if given solar date is valid & subsequently set the internal dates (lunar & solar) to the one given, if it is valid.

		Args:
			solar_year (int): Year
			solar_month (int): Month
			solar_day (int): Day

		Returns:
			bool: Indicates if given solar date is valid
		"""
		is_valid:bool = False
		if self.__check_valid_date(False, False, solar_year, solar_month, solar_day) :
			self.solar_year = solar_year
			self.solar_month = solar_month
			self.solar_day = solar_day
			self.__set_lunar_date_by_solar_date(solar_year, solar_month, solar_day)
			is_valid = True
		return is_valid

	def __get_gap_ja(self) -> None:
		"""Set the gapja indexes for the stored lunar date (`self.lunar_year`, `self.lunar_month`, `self.lunar_day`, `self.is_intercalation`).

		Lunar-based.

		The gapja for a year, a month or a day is composed of a Cheongan (stem, sky) among 10 (cardinal color and element are derived from it) and a Ganji (branch, earth) among 12 (also corresponding to the Chinese Zodiac animals/signs)

		Gapja year index (`self.__gapjaYearInx`):
		* 0: Cheongan: 10 year cycle: index in the cycle [0-9]
		* 1: Ganji: 12 year cycle: index in the cycle [0-11]
		* 2: Unit: 0 (corresponding to year)

		Gapja month index (`self.__gapjaMonthInx`): based on month without considering lunar intercalation months
		* 0: Cheongan: 10 month cycle: index in the cycle [0-9]
		* 1: Ganji: 12 month cycle: index in the cycle [0-11]
		* 2: Unit: 1 (corresponding to month)

		Gapja day index (`self.__gapjaDayInx`):
		* 0: Cheongan: 10 day cycle: index the cycle [0-9]
		* 1: Ganji: 12 day cycle: index in the cycle [0-11]
		* 2: Unit: 2 (corresponding to day)

		NOTE: Lunar Intercalation months are ignored when determining the gapja for the month.

		"""
		abs_days:int = self.__get_lunar_abs_days(self.lunar_year, self.lunar_month, self.lunar_day, self.is_intercalation)
		if abs_days > 0 :
			self.__gapjaYearInx[0] = ((self.lunar_year + 6) - self.KOREAN_LUNAR_BASE_YEAR) % len(self.KOREAN_CHEONGAN)
			self.__gapjaYearInx[1] = ((self.lunar_year + 0) - self.KOREAN_LUNAR_BASE_YEAR) % len(self.KOREAN_GANJI)
			
			month_count = self.lunar_month
			month_count += 12 * (self.lunar_year - self.KOREAN_LUNAR_BASE_YEAR)
			self.__gapjaMonthInx[0] = (month_count + 3) % len(self.KOREAN_CHEONGAN)
			self.__gapjaMonthInx[1] = (month_count + 1) % len(self.KOREAN_GANJI)
			
			self.__gapjaDayInx[0] = (abs_days + 4) % len(self.KOREAN_CHEONGAN)
			self.__gapjaDayInx[1] = (abs_days + 2) % len(self.KOREAN_GANJI)


	def _get_gap_ja_str(self, gapja_type:str) -> str:
		"""Get the characters associated with the stored gapja indexes in the chosen language.

		Args:
			gapja_type (str): ISO 3166 of Korea ('KR') or China ('CN')

		Raises:
			ValueError: If **gapja_type** is not valid

		Returns:
			str: `CGU CGU CGU` or `CGU CGU CGU (IU)` where:
				* `C`: Cheongan character
				* `G`: Ganji character
				* `U`: Unit character
				* `I`: Intercalation/Leap character
		"""
		_kr = ('KR',)
		_cn = ('CN',)
		if gapja_type in _kr:
			cheongan:tuple[int, ...] = self.KOREAN_CHEONGAN
			ganji: tuple[int, ...] = self.KOREAN_GANJI
			gapja_unit:tuple[int, ...] = self.KOREAN_GAPJA_UNIT
			intercalation_str:int = self.INTERCALATION_STR[0]
		elif gapja_type in _cn:
			cheongan = self.CHINESE_CHEONGAN
			ganji = self.CHINESE_GANJI
			gapja_unit = self.CHINESE_GAPJA_UNIT
			intercalation_str = self.INTERCALATION_STR[1]
		else:
			raise ValueError(f"gapja_type is:{gapja_type}\nShould be:\nKorean: {_kr} OR Chinese: {_cn}")
		gapja_str:str = "%c%c%c %c%c%c %c%c%c" % (chr(cheongan[self.__gapjaYearInx[0]]), chr(ganji[self.__gapjaYearInx[1]]), chr(gapja_unit[self.__gapjaYearInx[2]]),
		chr(cheongan[self.__gapjaMonthInx[0]]), chr(ganji[self.__gapjaMonthInx[1]]), chr(gapja_unit[self.__gapjaMonthInx[2]]),
		chr(cheongan[self.__gapjaDayInx[0]]), chr(ganji[self.__gapjaDayInx[1]]), chr(gapja_unit[self.__gapjaDayInx[2]]))

		if self.is_intercalation:
			gapja_str += " (%c%c)" % (chr(intercalation_str), chr(gapja_unit[1]))
		return gapja_str

	def get_gap_ja_string(self) -> str:
		"""Get Korean gapja string for stored lunar date.

		Returns:
			str: `CGU CGU CGU` or `CGU CGU CGU (IU)` where:
				* `C`: Cheongan character
				* `G`: Ganji character
				* `U`: Unit character
				* `I`: Intercalation/Leap character
		"""
		self.__get_gap_ja()
		gapja_str:str = self._get_gap_ja_str(gapja_type='KR')
		return gapja_str
		

	def get_chinese_gap_ja_string(self) -> str:
		"""Get Chinese gapja string for stored lunar date.

		Returns:
			str: `CGU CGU CGU` or `CGU CGU CGU (IU)` where:
				* `C`: Cheongan character
				* `G`: Ganji character
				* `U`: Unit character
				* `I`: Intercalation/Leap character
		"""
		self.__get_gap_ja()
		gapja_str:str = self._get_gap_ja_str(gapja_type='CN')

		return gapja_str

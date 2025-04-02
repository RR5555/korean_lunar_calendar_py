"""Test `korean_lunar_calendar`."""

import pytest
# import msgspec
import datetime

from korean_lunar_calendar.korean_lunar_calendar import KoreanLunarCalendar

class TestKoreanLunarCalendar():

	klc:KoreanLunarCalendar


	# def setup(self):
	# 	self.klc = KoreanLunarCalendar()

	def setup_method(self):
		self.klc = KoreanLunarCalendar()


	@pytest.mark.parametrize("year, month, day, res_weekday", [
		(2025, 3, 8, 5), # Greg: Sat(5)
		(1582, 10, 1, 4), # Jul: Mon(0), Greg: Fri(4)
		(1582, 10, 10, 6), # Jul: Wed(2), Greg: Sun(6)
		(1582, 12, 10, 4), # Jul: Mon(0), Greg: Fri(4)
		(1582, 10, 31, 6), # Jul: Wed(2), Greg: Sun(6)
		(1600, 1, 1, 5) # Jul: Tue(1), Greg: Sat(5)
	])
	def test_datetime_greg_proleptic(self, year:int, month:int, day:int, res_weekday:int):
		_date = datetime.datetime(year, month, day)
		assert _date.weekday() == res_weekday
		_delta:datetime.timedelta = _date - (datetime.datetime(self.klc.KOREAN_LUNAR_BASE_YEAR, 1, 1)+ datetime.timedelta(days=self.klc.SOLAR_LUNAR_DAY_DIFF))
		assert _delta.days == getattr(self.klc, '_KoreanLunarCalendar__get_solar_abs_days')(year, month, day) - 1



	@pytest.mark.parametrize("dates, intercalation, res", [((2025, 2, 26), False, "2025-02-26"), ((54, 11, 26), True, "0054-11-26 Intercalation")])
	def test_lunar_iso_format(self, dates:tuple[int, int, int], intercalation:bool, res:str) -> None:
		self.klc.lunar_year, self.klc.lunar_month, self.klc.lunar_day = dates
		self.klc.is_intercalation = intercalation
		assert self.klc.lunar_iso_format() == res

	@pytest.mark.parametrize("dates, intercalation, res", [((2025, 2, 26), False, "2025-02-26"), ((54, 11, 26), True, "0054-11-26")])
	def test_solar_iso_format(self, dates:tuple[int, int, int], intercalation:bool, res:str):
		self.klc.solar_year, self.klc.solar_month, self.klc.solar_day = dates
		self.klc.is_intercalation = intercalation
		assert self.klc.solar_iso_format() == res

	@pytest.mark.parametrize("year, res", [(1000, 0x82c60a57), (1001, 0x82fec52b), (1586, 0x82c40d4a), (2022, 0x82c60ad5), (2025, 0x83006a6e), (2049, 0x82c60ada), (2050, 0x830138b6)])
	def test_get_lunar_data(self, year:int, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_lunar_data')(year) == res


	@pytest.mark.parametrize("lunar_data, res", [
		(0b1111_1111_1111_1111_1001_1111_1111_1111, 0b1001),
		(0b1111_1111_1111_1111_1011_1111_1111_1111, 0b1011),
		(0b1111_1111_1111_1111_1001_0000_0000_0000, 0b1001),
		(0b1111_1111_1111_1111_0101_0000_0000_0000, 0b0101),
		(0b0000_0000_0000_0000_0101_0000_0000_0000, 0b0101)
	])
	def test__get_lunar_intercalation_month(self, lunar_data:int, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_lunar_intercalation_month')(lunar_data) == res




	@pytest.mark.parametrize("lunar_data, month, is_intercalation, res", [
		# Test if is_intercalation and (self.__get_lunar_intercalation_month(lunar_data) == month):
		(0b1111_1111_1111_1110_0001_1111_1111_1111, 1, True, 29),
		(0b1111_1111_1111_1111_0001_1111_1111_1111, 1, True, 30),
		(0b0000_0000_0000_0000_0001_0000_0000_0000, 1, True, 29),
		(0b0000_0000_0000_0001_0001_0000_0000_0000, 1, True, 30),
		# Test related else
		(0b1111_1111_1111_1110_0001_1111_1111_1111, 1, False, 30),
		(0b0000_0000_0000_0001_0001_0000_0000_0000, 1, False, 29),
		(0b0000_0000_0000_0001_0001_0000_0000_0000, 2, True, 29),
		(0b0000_0000_0000_0001_0001_0100_0000_0000, 2, True, 30),
		(0b1111_1111_1111_1111_0001_1011_1111_1111, 2, True, 29),
		(0b1111_1111_1111_1111_0001_1111_1111_1111, 2, True, 30),
		# Test year duration
		(0b1111_1100_1010_0001_1111_1111_1111_1111, None, None, 0b00_1010_000),
		(0b1111_1110_1001_0101_1111_1111_1111_1111, None, None, 0b10_1001_010),
		(0b0000_0000_1010_0000_0000_0000_0000_0000, None, None, 0b00_1010_000),
		(0b0000_0010_1001_0100_0000_0000_0000_0000, None, None, 0b10_1001_010),
		(0b1111_1100_0000_0001_1111_1111_1111_1111, None, None, 0b00_0000_000),
		(0b1111_1111_1111_1111_1111_1111_1111_1111, None, None, 0b11_1111_111),
		(0b0000_0011_1111_1110_0000_0000_0000_0000, None, None, 0b11_1111_111),
		(0b0000_0000_0000_0000_0000_0000_0000_0000, None, None, 0b00_0000_000),
	])
	def test__get_lunar_days_(self, lunar_data:int, month:int|None, is_intercalation:bool|None, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_lunar_days_')(lunar_data, month, is_intercalation) == res


	@pytest.mark.parametrize("year, month, is_intercalation, res", [
		(2025, 1, False, 30),
		(2025, 2, True, 29),
		(2025, None, False, 384),
	])
	def test__get_lunar_days(self, year:int, month:int|None, is_intercalation:bool|None, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_lunar_days')(year, month, is_intercalation) == res

	@pytest.mark.parametrize("year, res", [
		(1000, 355),
		(1001, 738),
		(2025, 374743),
	])
	def test__get_lunar_days_before_base_year(self, year:int, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_lunar_days_before_base_year')(year) == res


	@pytest.mark.parametrize("year, month, is_intercalation, res", [
		# Default cases
		(950, 1, True, 0),
		(1005, 0, True, 0),
		(2025, 13, False, 0),
		# Control & use cases
		(1005, 1, True, 29),
		(1000, 1, True, 30),
		(2025, 5, True, 147),
		(2025, 5, False, 147),
		(2025, 12, False, 355),
		(2025, 12, True, 384),
	])
	def test__get_lunar_days_before_base_month(self, year:int, month:int, is_intercalation:bool, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_lunar_days_before_base_month')(year, month, is_intercalation) == res


	@pytest.mark.parametrize("year, month, day, is_intercalation, res", [
		# 2025 has lunar intercalation [29 days] in June [30 days] 
		(2025, 1, 1, True, 374360),
		(2025, 12, 29, True, 374743),
		(2025, 5, 29, True, 374506),
		# (2025, 5, 32, True, 374509), #This should produce an error
		(2025, 6, 1, True, 374537),
		(2025, 6, 1, False, 374507),


		# 2022 has no intercalation
		(2002, 12, 30, True, 366327),
		(2002, 12, 30, False, 366327),

		# Other samples
		(1000, 1, 1, True, 1),
		(1000, 1, 1, False, 1),

		(1950, 9, 8, False, 347228),
		(1879, 6, 7, True, 321211)
	])
	def test__get_lunar_abs_days(self, year:int, month:int, day:int, is_intercalation:bool, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_lunar_abs_days')(year, month, day, is_intercalation) == res

	@pytest.mark.parametrize("lunar_data, res", [
		
		(0b1111_1111_1111_1111_1111_1111_1111_1111, True),
		(0b1011_1111_1111_1111_1111_1111_1111_1111, False),
		(0b0000_0000_0000_0000_0001_0000_0000_0000, False),
		(0b0100_0000_0000_0000_0001_0000_0000_0000, True),
	])
	def test__is_solar_intercalation_year(self, lunar_data:int, res:bool) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__is_solar_intercalation_year')(lunar_data) == res

	@pytest.mark.parametrize("lunar_data, month, res", [
		
		(0b1011_1111_1111_1111_1111_1111_1111_1111, 1, 31),
		(0b0000_0000_0000_0000_0000_0000_0000_0000, 1, 31),
		(0b1111_1111_1111_1111_1111_1111_1111_1111, 1, 31),
		(0b0100_0000_0000_0000_0000_0000_0000_0000, 1, 31),
		(0b1111_1111_1111_1111_1111_1111_1111_1111, 2, 29),
		(0b0100_0000_0000_0000_0000_0000_0000_0000, 2, 29),
		(0b1011_1111_1111_1111_1111_1111_1111_1111, 2, 28),
		(0b0000_0000_0000_0000_0000_0000_0000_0000, 2, 28),
		(0b1111_1111_1111_1111_1111_1111_1111_1111, None, 366),
		(0b0100_0000_0000_0000_0000_0000_0000_0000, None, 366),
		(0b1011_1111_1111_1111_1111_1111_1111_1111, None, 365),
		(0b0000_0000_0000_0000_0000_0000_0000_0000, None, 365),

		# month, and day validity are not checked as it is a private method, and not supposed to be exposed directly
		# Thus, the following test values will results in errors:
		# (0b1111_1111_1111_1111_1111_1111_1111_1111, 13, 366),
		# (0b0100_0000_0000_0000_0000_0000_0000_0000, 13, 366),
		# (0b1011_1111_1111_1111_1111_1111_1111_1111, 13, 365),
		# (0b0000_0000_0000_0000_0000_0000_0000_0000, 13, 365),
		# (0b1111_1111_1111_1111_1111_1111_1111_1111, -1, 366),
		# (0b0100_0000_0000_0000_0000_0000_0000_0000, -1, 366),
		# (0b1011_1111_1111_1111_1111_1111_1111_1111, -1, 365),
		# (0b0000_0000_0000_0000_0000_0000_0000_0000, -1, 365),

	])
	def test__get_solar_days_(self, lunar_data:int, month:int|None, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_solar_days_')(lunar_data, month) == res

	@pytest.mark.parametrize("year, month, res", [
		
		(2025, 4, 30),
		(2025, 12, 31),
		(2025, 2, 28),
		(2048, 2, 29),

		# 1582
		(1582, 10, 31),
		(1582, 12, 31),
		(1582, None, 365),

		# 1752
		(1752, None, 366),


		# 1896
		(1896, None, 366),


	])
	def test__get_solar_days(self, year:int, month:int|None, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_solar_days')(year, month) == res

	@pytest.mark.parametrize("year, res", [
		
		(1000, 365),
		(1001, 730),
		(1002, 1095),
		(1003, 1460),
		(1004, 1826), #intercalation year
		(1008, 3287), #intercalation year
		(2000, 365608),
		(2025, 374739)
	])
	def test__get_solar_days_before_base_year(self, year:int, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_solar_days_before_base_year')(year) == res

	@pytest.mark.parametrize("year, month, res", [
		
		(1000, 1, 31),
		(1000, 2, 59),
		(1000, 3, 90),
		(1000, 12, 365),

		#intercalation year
		(1004, 1, 31),
		(1004, 2, 60),
		(1004, 3, 91),
		(1004, 12, 366),

	])
	def test__get_solar_days_before_base_month(self, year:int, month:int, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_solar_days_before_base_month')(year, month) == res

	@pytest.mark.parametrize("year, month, day, res", [
		
		(1000, 2, 13, 1),
		(1000, 2, 14, 2),
		(1000, 2, 25, 13),
		(1000, 12, 31, 322), # 365-43

		# 1582
		(1582, 10, 1, 212802),
		(1582, 10, 3, 212804),
		(1582, 10, 4, 212805),
		(1582, 10, 5, 212806),
		(1582, 10, 8, 212809),
		(1582, 10, 13, 212814),
		(1582, 10, 14, 212815),
		(1582, 10, 15, 212816),


		(1356, 4, 27, 130101),
		(2024, 6, 13, 374130),

	])
	def test__get_solar_abs_days(self, year:int, month:int, day:int, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_solar_abs_days')(year, month, day) == res


	@pytest.mark.parametrize("lunar_year, lunar_month, lunar_day, is_intercalation, res", [
		
		(1000, 1, 1, True, (1000, 2, 13)),
		(1000, 1, 2, True, (1000, 2, 14)),
		# Lunar new year 2025/01/29
		(2025, 1, 1, True, (2025, 1, 29)),
		(2025, 1, 1, False, (2025, 1, 29)),
		# June 2025 leap month
		(2025, 5, 29, True,  (2025, 6, 24)),
		(2025, 5, 29, False, (2025, 6, 24)),
		(2025, 6, 1, True,   (2025, 7, 25)),
		(2025, 6, 1, False,  (2025, 6, 25)),
		(2025, 6, 2, True,   (2025, 7, 26)),
		(2025, 6, 2, False,  (2025, 6, 26)),
		(2025, 6, 30, True,  (2025, 8, 23)), # Notice ovelap with result of (2025, 7, 1) cause intercalation month is only 29 days not 30!
		(2025, 6, 30, False, (2025, 7, 24)),
		(2025, 7, 1, True,   (2025, 8, 23)),
		(2025, 7, 1, False,  (2025, 8, 23)),

		# Chuseok 2025/10/06
		(2025, 8, 15, True, (2025, 10, 6)),
		(2025, 8, 15, False, (2025, 10, 6)),


		(2025, 10, 8, True, (2025, 11, 27)),
		(2025, 10, 9, False, (2025, 11, 28)),


		(2026, 1, 1, True, (2026, 2, 17)),
		(2026, 1, 1, False, (2026, 2, 17)),

	])
	def test__set_solar_date_by_lunar_date(self, lunar_year:int, lunar_month:int, lunar_day:int, is_intercalation:bool, res:tuple[int, int, int]) -> None:
		getattr(self.klc, '_KoreanLunarCalendar__set_solar_date_by_lunar_date')(lunar_year, lunar_month, lunar_day, is_intercalation)
		assert (self.klc.solar_year, self.klc.solar_month, self.klc.solar_day) == res

	@pytest.mark.parametrize("year, month, day, is_intercalation", [
		
		(1000, 2, 13, True),
		(1000, 2, 13, False),
		(2025, 12, 20, True),
		(2025, 12, 20, False),
		(2025, 6, 13, True),
		(2025, 6, 13, False),

	])
	def test__solar_lunar_bijection(self, year:int, month:int, day:int, is_intercalation:bool) -> None:
		getattr(self.klc, '_KoreanLunarCalendar__set_solar_date_by_lunar_date')(year, month, day, is_intercalation)
		getattr(self.klc, '_KoreanLunarCalendar__set_lunar_date_by_solar_date')(self.klc.solar_year, self.klc.solar_month, self.klc.solar_day)
		assert (self.klc.lunar_year, self.klc.lunar_month, self.klc.lunar_day) == (year, month, day)

		getattr(self.klc, '_KoreanLunarCalendar__set_lunar_date_by_solar_date')(year, month, day)
		getattr(self.klc, '_KoreanLunarCalendar__set_solar_date_by_lunar_date')(self.klc.lunar_year, self.klc.lunar_month, self.klc.lunar_day, is_intercalation)
		assert (self.klc.solar_year, self.klc.solar_month, self.klc.solar_day) == (year, month, day)

	@pytest.mark.parametrize("solar_year, solar_month, solar_day, res", [
		
		(1000, 2, 13, (1000, 1, 1, False)),
		(1000, 2, 14, (1000, 1, 2, False)),
		# Lunar new year 2025/01/29
		(2025, 1, 29, (2025, 1, 1, False)),
		# June 2025 leap month
		(2025, 6, 24, (2025, 5, 29, False)),
		(2025, 7, 25, (2025, 6, 1, True)),
		(2025, 6, 25, (2025, 6, 1, False)),
		(2025, 7, 26, (2025, 6, 2, True)),
		(2025, 6, 26, (2025, 6, 2, False)),
		(2025, 7, 24, (2025, 6, 30, False)),
		(2025, 8, 23, (2025, 7, 1, False)),


		# Chuseok 2025/10/06
		(2025, 10, 6, (2025, 8, 15, False)),

		(2025, 11, 27, (2025, 10, 8, False)),
		(2025, 11, 28, (2025, 10, 9, False)),
		
		(2026, 2, 17, (2026, 1, 1, False)),

	])
	def test__set_lunar_date_by_solar_date(self, solar_year:int, solar_month:int, solar_day:int, res:tuple[int, int, int, bool]) -> None:
		getattr(self.klc, '_KoreanLunarCalendar__set_lunar_date_by_solar_date')(solar_year, solar_month, solar_day)
		assert (self.klc.lunar_year, self.klc.lunar_month, self.klc.lunar_day, self.klc.is_intercalation) == res

	@pytest.mark.parametrize("is_lunar, is_intercalation, year, month, day, res", [
		
		# Test Intercalation
		(True, False, 1000, 1, 1, True),
		(True, True, 1000, 1, 1, False),
		(True, True, 2025, 1, 1, False),
		(False, True, 2025, 1, 1, True),

		# 2025 Jun [30 days], June intercalation month [29 days]
		(True, True, 2025, 6, 29, True),
		(True, True, 2025, 6, 30, False),
		(True, False, 2025, 6, 30, True),

		# Month bound
		(False, False, 2025, 1, 1, True),
		(False, False, 2025, -1, 1, False),
		(False, False, 2025, 12, 31, True),
		(False, False, 2025, 13, 1, False),
		(True, False, 2025, 1, 1, True),
		(True, False, 2025, -1, 1, False),
		(True, False, 2025, 12, 29, True),
		(True, False, 2025, 13, 1, False),

		# Day bound
		(False, False, 2025, 1, 0, False),
		(False, False, 2025, 1, 32, False),
		(False, False, 2025, 2, 30, False),

		(True, False, 2025, 1, 0, False),
		(True, False, 2025, 1, 31, False),

		# Year bound
		(True, False, 1000, 1, 1, True),
		(True, False, 999, 12, 29, False),
		(False, False, 1000, 2, 13, True),
		(False, False, 1000, 2, 12, False),


	])
	def test__check_valid_date(self, is_lunar:bool, is_intercalation:bool, year:int, month:int, day:int, res:bool) -> None: # noqa: PLR0913
		assert getattr(self.klc, '_KoreanLunarCalendar__check_valid_date')(is_lunar, is_intercalation, year, month, day) == res



	@pytest.mark.parametrize("lunar_year, lunar_month, lunar_day, is_intercalation, is_valid, res", [
		
		(1000, 1, 1, False, True, (1000, 2, 13, 1000, 1, 1, False)),
		(999, 1, 1, False, False, (0, 1, 1, 0, 1, 1, False)),

	])
	def test_set_lunar_date(self, lunar_year:int, lunar_month:int, lunar_day:int, is_intercalation:bool, is_valid:bool, res:tuple[int, int, int, int, int, int, bool]) -> None: # noqa: PLR0913
		assert self.klc.set_lunar_date(lunar_year, lunar_month, lunar_day, is_intercalation) == is_valid
		assert (self.klc.solar_year, self.klc.solar_month, self.klc.solar_day, self.klc.lunar_year, self.klc.lunar_month, self.klc.lunar_day, self.klc.is_intercalation) == res

	@pytest.mark.parametrize("solar_year, solar_month, solar_day, is_valid, res", [
		
		(1000, 2, 13, True, (1000, 2, 13, 1000, 1, 1, False)),
		(1000, 2, 12, False, (0, 1, 1, 0, 1, 1, False)),

	])
	def test_set_solar_date(self, solar_year:int, solar_month:int, solar_day:int, is_valid:bool, res:tuple[int, int, int, int, int, int, bool]) -> None:
		assert self.klc.set_solar_date(solar_year, solar_month, solar_day) == is_valid
		assert (self.klc.solar_year, self.klc.solar_month, self.klc.solar_day, self.klc.lunar_year, self.klc.lunar_month, self.klc.lunar_day, self.klc.is_intercalation) == res


	@pytest.mark.parametrize("lunar_year, lunar_month, lunar_day, is_intercalation, gapja_year_inx, gapja_month_inx, gapja_day_inx", [
		
		(1000, 1, 1, False, [6, 0, 0], [4, 2, 1], [5, 3, 2]),

	])
	def test__get_gap_ja(self, lunar_year:int, lunar_month:int, lunar_day:int, is_intercalation:bool, gapja_year_inx:list[int], gapja_month_inx:list[int], gapja_day_inx:list[int]) -> None: # noqa: PLR0913
		self.klc.set_lunar_date(lunar_year, lunar_month, lunar_day, is_intercalation)
		getattr(self.klc, '_KoreanLunarCalendar__get_gap_ja')()
		assert getattr(self.klc, '_KoreanLunarCalendar__gapjaYearInx') == gapja_year_inx
		assert getattr(self.klc, '_KoreanLunarCalendar__gapjaMonthInx') == gapja_month_inx
		assert getattr(self.klc, '_KoreanLunarCalendar__gapjaDayInx') == gapja_day_inx


	@pytest.mark.parametrize("idx, res", [
		(0, "갑"),
		(1, "을"),
		(2, "병"),
		(3, "정"),
		(4, "무"),
		(5, "기"),
		(6, "경"),
		(7, "신"),
		(8, "임"),
		(9, "계"),
	])
	def test_kr_cheongan_string(self, idx:int, res:str) -> None:
		assert chr(self.klc.KOREAN_CHEONGAN[idx]) == res

	@pytest.mark.parametrize("idx, res", [
		(0, "자"),
		(1, "축"),
		(2, "인"),
		(3, "묘"),
		(4, "진"),
		(5, "사"),
		(6, "오"),
		(7, "미"),
		(8, "신"),
		(9, "유"),
		(10, "술"),
		(11, "해"),
	])
	def test_kr_ganji_string(self, idx:int, res:str) -> None:
		assert chr(self.klc.KOREAN_GANJI[idx]) == res

	@pytest.mark.parametrize("idx, res", [
		(0, "甲"),
		(1, "乙"),
		(2, "丙"),
		(3, "丁"),
		(4, "戊"),
		(5, "己"),
		(6, "庚"),
		(7, "辛"),
		(8, "壬"),
		(9, "癸"),
	])
	def test_cn_cheongan_string(self, idx:int, res:str) -> None:
		assert chr(self.klc.CHINESE_CHEONGAN[idx]) == res

	@pytest.mark.parametrize("idx, res", [
		(0, "子"),
		(1, "丑"),
		(2, "寅"),
		(3, "卯"),
		(4, "辰"),
		(5, "巳"),
		(6, "午"),
		(7, "未"),
		(8, "申"),
		(9, "酉"),
		(10, "戌"),
		(11, "亥"),
	])
	def test_cn_ganji_string(self, idx:int, res:str) -> None:
		assert chr(self.klc.CHINESE_GANJI[idx]) == res


	@pytest.mark.parametrize("lunar_year, lunar_month, lunar_day, is_intercalation, res", [
		
		(2025, 1, 1, False, "을사년 무인월 무술일"), # Indeed: 2025: Wood Snake
		(2025, 6, 1, True, "을사년 계미월 을미일 (윤월)"),
	])
	def test_get_gap_ja_string(self, lunar_year:int, lunar_month:int, lunar_day:int, is_intercalation:bool, res:str) -> None:
		self.klc.set_lunar_date(lunar_year, lunar_month, lunar_day, is_intercalation)
		assert self.klc.get_gap_ja_string() == res

	@pytest.mark.parametrize("lunar_year, lunar_month, lunar_day, is_intercalation, res", [
		
		(2025, 1, 1, False, "乙巳年 戊寅月 戊戌日"),
		(2025, 6, 1, True, "乙巳年 癸未月 乙未日 (閏月)"),
	])
	def test_get_chinese_gap_ja_string(self, lunar_year:int, lunar_month:int, lunar_day:int, is_intercalation:bool, res:str) -> None:
		self.klc.set_lunar_date(lunar_year, lunar_month, lunar_day, is_intercalation)
		assert self.klc.get_chinese_gap_ja_string() == res




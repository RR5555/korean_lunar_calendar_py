
import pytest
# import msgspec

from kr_holidays.korean_lunar_calendar import KoreanLunarCalendar


class TestKoreanLunarCalendar():

	klc:KoreanLunarCalendar


	# @pytest.fixture(scope='class', autouse=True)
	# @classmethod
	# def setup_and_teardown(cls):
	def setup_class(cls):
		cls.klc = KoreanLunarCalendar()
		# yield

	

	# @classmethod
	# def teardown_class(cls):
	# 	cls.info("starting class: {} execution".format(cls.__name__))

	# def setup(self):
	# 	self.klc = KoreanLunarCalendar()

	# @pytest.mark.parametrize("dates, error_msg", [((1991, 1, 11), None), ((1991, 12, 31), None), ((1000, 1, 1), None), ((2025, -1, 26), ""), ((1802, 14, 18), ""), ((1802, 7, -8), ""), ((1537, 6, 34), "")])
	# def test_init_solar(self, dates:tuple[int, int, int], error_msg:str|None):
		# if error_msg is not None:
		# 	with pytest.raises(msgspec.ValidationError) as val_error:
		# 		self.klc.solar_year, self.klc.solar_month, self.klc.solar_day = dates
		# 	print(val_error)
		# 	# assert val_error.value.__str__() == error_msg
		# else:
		# 	self.klc.solar_year, self.klc.solar_month, self.klc.solar_day = dates

		# self.klc.solar_year, self.klc.solar_month, self.klc.solar_day = dates

		# print(f"{self.klc.solar_year}, {self.klc.solar_month}, {self.klc.solar_day}")


	# def test_lunar_intercalation_duration_data(self):
	# 	for _idx, _lunar_data in enumerate(self.klc.KOREAN_LUNAR_DATA):
	# 		# _bit:int = (_lunar_data >>16) & 0b01
	# 		# assert _bit == 0, f"{_idx+1000}:{_lunar_data:0b}"
	# 		_intercal_month:int = (_lunar_data >>12) & 0b1111
	# 		if 13 >_intercal_month > 0:
	# 			_month_duration:int = (_lunar_data >>12-_intercal_month) & 0b01
	# 			_intercalation_duration:int = (_lunar_data >>16) & 0b01
	# 			assert (_month_duration == 1 or _month_duration==_intercalation_duration), f"{_idx+1000}:{_lunar_data:0b}"


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
		(2048, 2, 29)
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
		
		(True, False, 1000, 1, 1, True),
		(True, True, 1000, 1, 1, True), # It is not checked whether intercalation is correct...

	])
	def test__check_valid_date(self, is_lunar:bool, is_intercalation:bool, year:int, month:int, day:int, res:bool) -> None: # noqa: PLR0913
		assert getattr(self.klc, '_KoreanLunarCalendar__check_valid_date')(is_lunar, is_intercalation, year, month, day) == res



	# @pytest.mark.parametrize("solar_year, solar_month, solar_day, res", [
		
	# 	(1000, 1, 1, True, (1000, 2, 13)),
	# 	(1000, 1, 2, True, (1000, 2, 14)),
	# 	(2025, 10, 8, True, (2025, 11, 27)),
	# 	(2025, 10, 9, False, (2025, 11, 28)),

	# ])
	# def test__set_solar_date_by_lunar_date(self, solar_year:int, solar_month:int, solar_day:int, res:tuple[int, int, int, int]) -> None:
	# 	getattr(self.klc, '_KoreanLunarCalendar__set_solar_date_by_lunar_date')(solar_year, solar_month, solar_day)
	# 	assert (self.klc.lunar_year, self.klc.lunar_month, self.klc.lunar_day, self.klc.is_intercalation) == res



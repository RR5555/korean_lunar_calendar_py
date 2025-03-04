
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

	@pytest.mark.parametrize("year, res", [(1000, 0x82c60a57), (1001, 0x82fec52b), (1586, 0x82c40d4a), (2022, 0x82c60ad5), (2049, 0x82c60ada), (2050, 0x830138b6)])
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
		(1000, 1, True, 355),
	])
	def test__get_lunar_days_before_base_month(self, year:int, month:int, is_intercalation:bool, res:int) -> None:
		assert getattr(self.klc, '_KoreanLunarCalendar__get_lunar_days_before_base_month')(year) == res






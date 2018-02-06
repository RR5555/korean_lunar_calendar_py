# korean_lunar_calendar_py
한국 양음력 변환

#### Overview
Here is a library to convert Korean lunar-calendar to Gregorian calendar.

Korean calendar and Chinese calendar is same lunar calendar but have different date.

This follow the KARI(Korea Astronomy and Space Science Institute)

한국 양음력 변환 (한국천문연구원 기준) - 네트워크 연결 불필요

음력 변환은 1391년 1월 1일 부터 2050년 11월 18일까지 지원

````
Gregorian calendar (1391. 2. 5. ~ 2050. 12. 31) <--> Korean lunar-calendar (1391. 1. 1. ~ 2050. 11. 18)
````
#### Install

pip install korean_lunar_calendar

#### To use

(0) import module
```python
from korean_lunar_calendar import KoreanLunarCalendar
```

(1) Korean Solar Date -> Korean Lunar Date (양력 -> 음력)
```python
calendar = KoreanLunarCalendar()
# params : year(년), month(월), day(일)
calendar.setSolarDate(2017, 6, 24)
# Lunar Date (ISO Format)
print(calendar.LunarIsoFormat())
# Korean GapJa String
print(calendar.getGapJaString())
# Chinese GapJa String
print(calendar.getChineseGapJaString())
```

```
[Result]
2017-05-01 Intercalation
정유년 병오월 임오일 (윤월)
丁酉年 丙午月 壬午日 (閏月)
```

(2) Korean Lunar Date -> Korean Solar Date (음력 -> 양력)
```python
# params : year(년), month(월), day(일), intercalation(윤달여부)
calendar.setLunarDate(1956, 1, 21, False)
# Solar Date (ISO Format)
print(calendar.SolarIsoFormat())
# Korean GapJa String
print(calendar.getGapJaString())
# Chinese GapJa String
print(calendar.getChineseGapJaString())
```

```
[Result]
1956-03-03
병신년 경인월 기사일
丙申年 庚寅月 己巳日
```
import unittest
from math import isclose
from common.r3 import R3
from shadow.polyedr import Segment, Edge, Facet
from tests.matchers import R3ApproxMatcher, SegmentApproxMatcher


class TestVoid(unittest.TestCase):

    # Одномерной координате 0.0 соответствует начало ребра
    def test_r301(self):
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, -1.0))
        self.assertEqual(R3ApproxMatcher(s.beg), s.r3(0.0))

    # Одномерной координате 1.0 соответствует конец ребра
    def test_r302(self):
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, -1.0))
        self.assertEqual(R3ApproxMatcher(s.fin), s.r3(1.0))

    # Одномерной координате 0.5 соответствует середина ребра
    def test_r303(self):
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, -1.0))
        self.assertEqual(R3ApproxMatcher(R3(0.5, 0.0, -1.0)), s.r3(0.5))

    # Если ребро принадлежит полупространству, то пересечение — весь отрезок
    def test_intersect_01(self):
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, -1.0))
        a = R3(0.0, 0.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        self.assertEqual(
            SegmentApproxMatcher(s.intersect_edge_with_normal(a, n)),
            Segment(0.0, 1.0))

    # Если ребро лежит вне полупространства, то пересечение пусто
    def test_intersect_02(self):
        s = Edge(R3(0.0, 0.0, 1.0), R3(1.0, 0.0, 1.0))
        a = R3(0.0, 0.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        self.assertTrue(s.intersect_edge_with_normal(a, n).is_degenerate())

    # Если ребро принадлежит плоскости, ограничивающей полупространство,
    # то пересечение пусто
    def test_intersect_03(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 0.0, 0.0))
        a = R3(0.0, 0.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        self.assertTrue(s.intersect_edge_with_normal(a, n).is_degenerate())

    # Здесь только первая половина отрезка принадлежит полупространству
    def test_intersect_04(self):
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, 1.0))
        a = R3(1.0, 1.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        self.assertEqual(
            SegmentApproxMatcher(s.intersect_edge_with_normal(a, n)),
            Segment(0.0, 0.5))

    # Здесь только вторая половина отрезка принадлежит полупространству
    def test_intersect_05(self):
        s = Edge(R3(0.0, 0.0, 1.0), R3(1.0, 0.0, -1.0))
        a = R3(1.0, 1.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        self.assertEqual(SegmentApproxMatcher(s.intersect_edge_with_normal(
            a, n)), Segment(0.5, 1.0))

    # Грань не затеняет ребро, принадлежащее этой же грани
    def test_shadow_01(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 1.0, 0.0))
        f = Facet([R3(0.0, 0.0, 0.0), R3(2.0, 0.0, 0.0),
                   R3(2.0, 2.0, 0.0), R3(0.0, 2.0, 0.0)])
        s.shadow(f)
        self.assertEqual(SegmentApproxMatcher(s.gaps[0]), Segment(0.0, 1.0))

    # Грань не затеняет ребро, расположенное выше этой грани
    def test_shadow_02(self):
        s = Edge(R3(0.0, 0.0, 1.0), R3(1.0, 1.0, 1.0))
        f = Facet([R3(0.0, 0.0, 0.0), R3(2.0, 0.0, 0.0),
                   R3(2.0, 2.0, 0.0), R3(0.0, 2.0, 0.0)])
        s.shadow(f)
        self.assertEqual(SegmentApproxMatcher(s.gaps[0]), Segment(0.0, 1.0))

    # Грань полностью затеняет ребро, расположенное под этой гранью
    def test_shadow_03(self):
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 1.0, -1.0))
        f = Facet([R3(0.0, 0.0, 0.0), R3(2.0, 0.0, 0.0),
                   R3(2.0, 2.0, 0.0), R3(0.0, 2.0, 0.0)])
        s.shadow(f)
        self.assertEqual(len(s.gaps), 0)

    # На длинном ребре, лежащем ниже грани, образуется ровно два просвета
    def test_shadow_04(self):
        s = Edge(R3(-5.0, -5.0, -1.0), R3(3.0, 3.0, -1.0))
        f = Facet([R3(0.0, 0.0, 0.0), R3(2.0, 0.0, 0.0),
                   R3(2.0, 2.0, 0.0), R3(0.0, 2.0, 0.0)])
        s.shadow(f)
        self.assertEqual(len(s.gaps), 2)

    # «Вертикальная» грань не затеняет ничего
    def test_shadow_05(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 1.0, 0.0))
        f = Facet([R3(0.0, 0.0, 0.0), R3(0.0, 0.0, 1.0),
                   R3(0.0, 1.0, 1.0), R3(0.0, 1.0, 0.0)])
        s.shadow(f)
        self.assertEqual(len(s.gaps), 1)
        self.assertEqual(SegmentApproxMatcher(s.gaps[0]), Segment(0.0, 1.0))

    # Перпендикулярная грань не затеняет ничего
    def test_shadow_06(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(0.0, 0.0, -1.0))
        f = Facet([R3(0.0, 0.0, 0.0), R3(1.0, 0.0, 0.0),
                   R3(1.0, 1.0, 0.0), R3(0.0, 1.0, 0.0)])
        s.shadow(f)
        self.assertEqual(len(s.gaps), 1)
        self.assertEqual(SegmentApproxMatcher(s.gaps[0]), Segment(0.0, 1.0))

    # Проверка дополнительных методов

    # Проверка центра ребра

    # Центр ребра, параллельного Ox, лежит на 2.5 -> подходит
    def test_center_01(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(5.0, 0.0, 0.0))
        self.assertTrue(s.good_center())

    # Центр по оси Ox лежит на 1.5, остальное неважно
    def test_center_02(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(3.0, 456.0, 47.0))
        self.assertTrue(s.good_center())

    # Центра на оси Ox лежит на 3.0, но по условию строгое нер-во
    def test_center_03(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(6.0, -12.0, 63.9))
        self.assertFalse(s.good_center())

    # Проверка угла

    # Вертикальное ребро не подходит (угол pi/2)
    def test_angle_01(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(0.0, 0.0, 1.0))
        self.assertFalse(s.good_angle())

    # Ребро на оси Ox подходит (0 рад)
    def test_angle_02(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 0.0, 0.0))
        self.assertTrue(s.good_angle())

    # Ребро на оси Oy подходит (0 рад)
    def test_angle_03(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(0.0, 1.0, 0.0))
        self.assertTrue(s.good_angle())

    # Ребро на плоскости Oxy подходит (0 рад)
    def test_angle_04(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 1.0, 0.0))
        self.assertTrue(s.good_angle())

    # Тангенс угла меньше, чем 1/sqrt(3) и угол подходит
    def test_angle_05(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.75, 30.0, 1.0))
        self.assertTrue(s.good_angle())

    # Тангенс угла больше, чем 1/sqrt(3) и угол НЕ подходит
    def test_angle_06(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.8, 0.0, 1.0))
        self.assertFalse(s.good_angle())

    # Проверка проекции

    # Единичный по оси Oy
    def test_projection_01(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(0.0, 1.0, 0.0))
        self.assertEqual(s.projection_length(), 1.0)

    # Единичный по оси Ox
    def test_projection_02(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 0.0, 0.0))
        self.assertEqual(s.projection_length(), 1.0)

    # Про координату z «забываем»
    def test_projection_03(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 0.0, 47.0))
        self.assertEqual(s.projection_length(), 1.0)

    # Египетский треугольник
    def test_projection_04(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(3.0, 4.0, 0.0))
        self.assertEqual(s.projection_length(), 5.0)

    # sqrt(53) ~ 7.28
    def test_projection_05(self):
        s = Edge(R3(0.0, 0.0, 0.0), R3(2.0, 7.0, 0.0))
        self.assertAlmostEqual(s.projection_length(), 7.3, 1)

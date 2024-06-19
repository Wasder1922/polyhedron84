import unittest
from unittest.mock import patch, mock_open

from shadow.polyedr import Polyedr


class TestPolyedr(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        fake_file_content = """200.0	45.0	45.0	30.0
8	4	16
-0.5	-0.5	0.5
-0.5	0.5	0.5
0.5	0.5	0.5
0.5	-0.5	0.5
-0.5	-0.5	-0.5
-0.5	0.5	-0.5
0.5	0.5	-0.5
0.5	-0.5	-0.5
4	5    6    2    1
4	3    2    6    7
4	3    7    8    4
4	1    4    8    5"""
        fake_file_path = 'data/holey_box.geom'
        with patch('shadow.polyedr.open'.format(__name__),
                   new=mock_open(read_data=fake_file_content)) as _file:
            self.polyedr = Polyedr(fake_file_path)
            _file.assert_called_once_with(fake_file_path)

    def test_num_vertexes(self):
        self.assertEqual(len(self.polyedr.vertexes), 8)

    def test_num_facets(self):
        self.assertEqual(len(self.polyedr.facets), 4)

    def test_num_edges(self):
        self.assertEqual(len(self.polyedr.edges), 16)

    # Свои простые фигуры для тестов

    # Две грани, одна полностью помещает в тень другую,
    # притом у «нижней» два ребра длины 5 подходят
    def test_figure1(self):
        polyedr = Polyedr('data/figure1.geom')
        answer = polyedr.calculate_sum()
        self.assertEqual(answer, 10.0)

    # Всё те же две грани, но теперь повернуты так,
    # что одно подходящее по условиям ребро стало видимым
    # (поэтому длина теперь 5)
    def test_figure2(self):
        polyedr = Polyedr('data/figure2.geom')
        answer = polyedr.calculate_sum()
        self.assertEqual(answer, 5.0)

    # Всё те же две грани, но перевёрнуты
    # на pi радиан по оси Oy => все ребра
    # стали видны и ответ 0.0
    def test_figure3(self):
        polyedr = Polyedr('data/figure3.geom')
        answer = polyedr.calculate_sum()
        self.assertEqual(answer, 0.0)

    # Для одной грани нет затемненных рёбер,
    # значит и нет подходящих по условию
    def test_figure4(self):
        polyedr = Polyedr('data/figure4.geom')
        answer = polyedr.calculate_sum()
        self.assertEqual(answer, 0.0)

    # Вертикальная грань не отбрасывает тень по условию
    def test_figure5(self):
        polyedr = Polyedr('data/figure5.geom')
        answer = polyedr.calculate_sum()
        self.assertEqual(answer, 0.0)

    # Коэффициент гомотетии не изменяет сам полиэдр
    # файл идентиен с figure1 за исключением к. гомотетии
    def test_figure6(self):
        polyedr = Polyedr('data/figure6.geom')
        answer = polyedr.calculate_sum()
        self.assertEqual(answer, 10.0)

    # Коэффициент гомотетии не изменяет сам полиэдр
    # файл идентичен с figure2 за исключением к. гомотетии
    def test_figure7(self):
        polyedr = Polyedr('data/figure7.geom')
        answer = polyedr.calculate_sum()
        self.assertEqual(answer, 5.0)

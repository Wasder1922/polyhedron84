import math
from math import pi, sqrt
from functools import reduce
from operator import add
from common.r3 import R3
from common.tk_drawer import TkDrawer


class Segment:
    """ Одномерный отрезок """
    # Параметры конструктора: начало и конец отрезка (числа)

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin

    # Отрезок вырожден?
    def is_degenerate(self):
        return self.beg >= self.fin

    # Пересечение с отрезком
    def intersect(self, other):
        if other.beg > self.beg:
            self.beg = other.beg
        if other.fin < self.fin:
            self.fin = other.fin
        return self

    # Разность отрезков
    # Разность двух отрезков всегда является списком из двух отрезков!
    def subtraction(self, other):
        return [Segment(
            self.beg, self.fin if self.fin < other.beg else other.beg),
            Segment(self.beg if self.beg > other.fin else other.fin, self.fin)]


class Edge:
    """ Ребро полиэдра """
    # Начало и конец стандартного одномерного отрезка
    SBEG, SFIN = 0.0, 1.0

    # Параметры конструктора: начало и конец ребра (точки в R3)
    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin
        # Список «просветов»
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]

    # Учёт тени от одной грани
    def shadow(self, facet):
        # «Вертикальная» грань не затеняет ничего
        if facet.is_vertical():
            return
        # Нахождение одномерной тени на ребре
        shade = Segment(Edge.SBEG, Edge.SFIN)
        for u, v in zip(facet.vertexes, facet.v_normals()):
            shade.intersect(self.intersect_edge_with_normal(u, v))
            if shade.is_degenerate():
                return

        shade.intersect(
            self.intersect_edge_with_normal(
                facet.vertexes[0], facet.h_normal()))
        if shade.is_degenerate():
            return
        # Преобразование списка «просветов», если тень невырождена
        gaps = [s.subtraction(shade) for s in self.gaps]
        self.gaps = [
            s for s in reduce(add, gaps, []) if not s.is_degenerate()]

    # Преобразование одномерных координат в трёхмерные
    def r3(self, t):
        return self.beg * (Edge.SFIN - t) + self.fin * t

    # Пересечение ребра с полупространством, задаваемым точкой (a)
    # на плоскости и вектором внешней нормали (n) к ней
    def intersect_edge_with_normal(self, a, n):
        f0, f1 = n.dot(self.beg - a), n.dot(self.fin - a)
        if f0 >= 0.0 and f1 >= 0.0:
            return Segment(Edge.SFIN, Edge.SBEG)
        if f0 < 0.0 and f1 < 0.0:
            return Segment(Edge.SBEG, Edge.SFIN)
        x = - f0 / (f1 - f0)
        return Segment(Edge.SBEG, x) if f0 < 0.0 else Segment(x, Edge.SFIN)
    
    # Проверка всех условий (за исключением невидимости) для ребра

    # Центр ребра находится на расстоянии строго меньше
    # 1 от плоскости x = 2 (с учетом гомотетии и обратным преобразованием)
    def good_center(self, c=1.0, ugol1=0.0, ugol2=0.0, ugol3=0.0):
        beg = R3(self.beg.x, self.beg.y, self.beg.z)
        fin = R3(self.fin.x, self.fin.y, self.fin.z)
        original_beg = beg.rz(-ugol3).ry(-ugol2).rz(-ugol1)
        original_fin = fin.rz(-ugol3).ry(-ugol2).rz(-ugol1)
        center_point = R3((original_beg.x + original_fin.x) / 2,
                          (original_beg.y + original_fin.y) / 2,
                          (original_beg.z + original_fin.z) / 2)
        return True if 1 < center_point.x / c < 3 else False

    def good_angle(self, ugol1=0.0, ugol2=0.0, ugol3=0.0):
        limit_angle_v2 = math.cos(math.pi / 7) ** 2
        vector = R3(
            self.fin.x - self.beg.x,
            self.fin.y - self.beg.y,
            self.fin.z - self.beg.z)
        V = R3(0.0, 0.0, 1.0)
        cos_v2 = (V.dot(vector)**2) / (V.dot(V) * vector.dot(vector))
        need_cos_v2 = 1 - cos_v2
        return need_cos_v2 >= limit_angle_v2

    # Нахождение длины проекции ребра (с учетом гомотетии)
    def projection_length(self, c=1.0, ugol1=0.0, ugol2=0.0, ugol3=0.0):
        beg = R3(self.beg.x, self.beg.y, self.beg.z)
        fin = R3(self.fin.x, self.fin.y, self.fin.z)
        original_beg = beg.rz(-ugol3).ry(-ugol2).rz(-ugol1)
        original_fin = fin.rz(-ugol3).ry(-ugol2).rz(-ugol1)
        lenght = sqrt(
            (fin.x - beg.x)**2 + (fin.y - beg.y)**2)
        return lenght / c


class Facet:
    """ Грань полиэдра """
    # Параметры конструктора: список вершин

    def __init__(self, vertexes):
        self.vertexes = vertexes

    # «Вертикальна» ли грань?
    def is_vertical(self):
        return self.h_normal().dot(Polyedr.V) == 0.0

    # Нормаль к «горизонтальному» полупространству
    def h_normal(self):
        n = (
            self.vertexes[1] - self.vertexes[0]).cross(
            self.vertexes[2] - self.vertexes[0])
        return n * (-1.0) if n.dot(Polyedr.V) < 0.0 else n

    # Нормали к «вертикальным» полупространствам, причём k-я из них
    # является нормалью к грани, которая содержит ребро, соединяющее
    # вершины с индексами k-1 и k
    def v_normals(self):
        return [self._vert(x) for x in range(len(self.vertexes))]

    # Вспомогательный метод
    def _vert(self, k):
        n = (self.vertexes[k] - self.vertexes[k - 1]).cross(Polyedr.V)
        return n * \
            (-1.0) if n.dot(self.vertexes[k - 1] - self.center()) < 0.0 else n

    # Центр грани
    def center(self):
        return sum(self.vertexes, R3(0.0, 0.0, 0.0)) * \
            (1.0 / len(self.vertexes))


class Polyedr:
    """ Полиэдр """
    # вектор проектирования
    V = R3(0.0, 0.0, 1.0)

    # Параметры конструктора: файл, задающий полиэдр
    def __init__(self, file):

        # списки вершин, рёбер и граней полиэдра
        self.vertexes, self.edges, self.facets = [], [], []
        # self.original_vertexes, self.original_edges, self.original_facets = [], [], []
        self.sum = 0.0
        self.c = 0

        # список строк файла
        with open(file) as f:
            for i, line in enumerate(f):
                if i == 0:
                    # обрабатываем первую строку; buf - вспомогательный массив
                    buf = line.split()
                    # коэффициент гомотетии
                    c = float(buf.pop(0))
                    self.c = c
                    # углы Эйлера, определяющие вращение
                    self.alpha, self.beta, self.gamma = (float(x) * pi / 180.0 for x in buf)
                elif i == 1:
                    # во второй строке число вершин, граней и рёбер полиэдра
                    nv, nf, ne = (int(x) for x in line.split())
                elif i < nv + 2:
                    # задание всех вершин полиэдра
                    x, y, z = (float(x) for x in line.split())
                    self.vertexes.append(R3(x, y, z).rz(
                        self.alpha).ry(self.beta).rz(self.gamma) * c)
                    # self.original_vertexes.append(R3(x, y, z))
                else:
                    # вспомогательный массив
                    buf = line.split()
                    # количество вершин очередной грани
                    size = int(buf.pop(0))
                    # массив вершин этой грани
                    vertexes = list(self.vertexes[int(n) - 1] for n in buf)
                    # original_vertexes = list(self.original_vertexes[int(n) - 1] for n in buf)
                    # задание рёбер грани
                    for n in range(size):
                        self.edges.append(Edge(vertexes[n - 1], vertexes[n]))
                        # self.original_edges.append(Edge(original_vertexes[n - 1], original_vertexes[n]))
                    # задание самой грани
                    self.facets.append(Facet(vertexes))
                    # self.original_facets.append(Facet(original_vertexes))

    # Итоговый метод, считающий необходимую характеристику
    def calculate_sum(self):
        final_sum = 0.0
        for e in self.edges:
            for f in self.facets:
                e.shadow(f)
            if e.gaps == [] and e.good_center(self.c, self.alpha, self.beta, self.gamma) and e.good_angle(self.alpha, self.beta, self.gamma):
                final_sum += e.projection_length(self.c, self.alpha, self.beta, self.gamma)
        return final_sum

    # Метод изображения полиэдра
    def draw(self, tk):  # pragma: no cover
        tk.clean()
        for e in self.edges:
            for f in self.facets:
                e.shadow(f)
            # Мы проверили все тени и теперь можно проверить наши условия
            if e.gaps == [] and e.good_center(self.c, self.alpha, self.beta, self.gamma) and e.good_angle(self.alpha, self.beta, self.gamma):
                self.sum += e.projection_length(self.c, self.alpha, self.beta, self.gamma)
            for s in e.gaps:
                tk.draw_line(e.r3(s.beg), e.r3(s.fin))
        print('Сумма длин проекций рёбер, ' +
              f'удовлетворяющих условиям = {self.sum}')

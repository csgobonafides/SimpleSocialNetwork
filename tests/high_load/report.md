# Производительность индексов.


## Входные параметры

 - intel i5-13400, 32Gb
 - Количество записей в таблице users: 999_931
 - Количество запросов: 5_000


### Без использования индексов


|Потоки     | RPS      | Avg latency | Min latency | Max latency | Total time |
| :-------- |:---------|:------------|-------------|-------------|------------|
| 1         | 31.18    | 32.05ms     | 15.0ms      | 63.0ms      | 160.4s     |
| 10        | 102.99   | 94.87ms     | 31.0ms      | 204.0ms     | 48.5s      |
| 100       | 104.27   | 944.03ms    | 31.0ms      | 2625.0ms    | 48.0s      |
| 1000      | 100.03   | 8915.4ms    | 47.0ms      | 29562.0ms   | 50.0s      |

#### С использованием инекса B-Tree по полям (first_name, last_name, id)

|Потоки     | RPS       | Avg latency | Min latency | Max latency  | Total time |
| :-------- |:----------|:------------|-------------|--------------|------------|
| 1         | 253.37    | 3.79ms      | 0.0ms       | 63.0ms       | 19.7s      |
| 10        | 481.93    | 20.57ms     | 0.0ms       | 78.0ms       |  10.4s     |
| 100       | 493.1     | 185.31ms    | 0.0ms       | 1532.0ms     | 10.1s      |
| 1000      | 415.59    | 1580.86ms   | 0.0ms       | 10453.0ms    | 12.0s      |


### Explain запросов после индекса


```
Sort  (cost=8.47..8.47 rows=1 width=144) (actual time=0.153..0.154 rows=20 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 28kB
  ->  Index Scan using social_name_id_idx on social  (cost=0.42..8.46 rows=1 width=144) (actual time=0.076..0.148 rows=20 loops=1)
        Index Cond: (((first_name)::text ~>=~ 'Выс'::text) AND ((first_name)::text ~<~ 'Выт'::text) AND ((last_name)::text ~>=~ 'Пол'::text) AND ((last_name)::text ~<~ 'Пом'::text))
        Filter: (((first_name)::text ~~ 'Выс%'::text) AND ((last_name)::text ~~ 'Пол%'::text))
Planning Time: 0.239 ms
Execution Time: 0.165 ms
```


### Oбъяснение почему индекс именно такой

В PostgreSQL, для эффективного поиска поиск по префиксу с LIKE 'xxx%' по колонкам first_name, last_name и сортировкой по id подойдет составной B-Tree индекс.

- Префикс LIKE 'xxx% планировщик преобразует в диапазон WHERE first_name >= 'xxx' AND first_name < 'xxx' а так как B-Tree индекс — это сбалансированное дерево, то такой поиск работает эффективно, PostgreSQL находит стартовую точку и итерирует по отсортированным значениям.
- так же эффективно рабоатет сортировка ORDER BY id так как id это часть составного индекса
- при создании таблицы для полей first_name и last_name нужно указать COLLATE "C" для байтового сравнения, либо при создании индекса указать varchar_pattern_ops
Для подстрочных поисков лучше всего использовать GIN-индексы с расширением pg_trgm, которое позволяет эффективно искать по шаблонам в стиле %substring%.
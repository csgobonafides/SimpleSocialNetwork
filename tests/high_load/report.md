# Производительность индексов.


## Входные параметры

 - intel i5-13400, 32Gb
 - Количество записей в таблице users: 999_931
 - Количество запросов: 5_000


### Без использования индексов


|Потоки     |RPS       |Avg latency	|Min latency | Max latency | Total time |
| :-------- | :------- | :----------|------------|-------------|------------|
| 1         | 27.3     | 36.61ms    | 31.0ms     | 63.0ms      | 183.2s     |
| 10        | 700.28   | 13.39ms    | 0.0ms      | 125.0ms     | 7.1s       |
| 100       | 904.0    | 104.27ms   | 0.0ms      | 282.0ms     | 5.5s       |
| 1000      | 804.12   | 1128.21ms  | 266.0ms    | 1563.0ms    | 6.2s       |

#### С использованием инекса B-Tree по полям (first_name, last_name, id)

|Потоки     |RPS       |Avg latency	|Min latency | Max latency | Total time |
| :-------- | :------- | :----------|------------|-------------|------------|
| 1         | 246.34   | 3.76ms     | 0.0ms      | 32.0ms      | 20.3s      |
| 10        | 651.72   | 12.52ms    | 0.0ms      | 79.0ms      |  7.7s      |
| 100       | 732.28   | 106.96ms   | 0.0ms      | 266.0ms     | 6.8s       |
| 1000      | 582.89   | 1132.04ms  | 375.0ms    | 1500.0ms    | 8.6s       |


### Explain запросов после индекса


```
Sort  (cost=312.38..312.44 rows=25 width=974) (actual time=1.833..1.840 rows=197 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 56kB
  ->  Index Scan using social_name_id_idx on social  (cost=0.42..311.80 rows=25 width=974) (actual time=0.061..1.794 rows=197 loops=1)
        Index Cond: (((first_name)::text ~>=~ 'Его'::text) AND ((first_name)::text ~<~ 'Егп'::text) AND ((last_name)::text ~>=~ 'Арт'::text) AND ((last_name)::text ~<~ 'Ару'::text))
        Filter: (((first_name)::text ~~ 'Его%'::text) AND ((last_name)::text ~~ 'Арт%'::text))
Planning Time: 0.205 ms
Execution Time: 1.858 ms
```


### Oбъяснение почему индекс именно такой

В PostgreSQL, для эффективного поиска поиск по префиксу с LIKE 'xxx%' по колонкам first_name, last_name и сортировкой по id подойдет составной B-Tree индекс.

- Префикс LIKE 'xxx% планировщик преобразует в диапазон WHERE first_name >= 'xxx' AND first_name < 'xxx' а так как B-Tree индекс — это сбалансированное дерево, то такой поиск работает эффективно, PostgreSQL находит стартовую точку и итерирует по отсортированным значениям.
- так же эффективно рабоатет сортировка ORDER BY id так как id это часть составного индекса
- при создании таблицы для полей first_name и last_name нужно указать COLLATE "C" для байтового сравнения, либо при создании индекса указать varchar_pattern_ops
Для подстрочных поисков лучше всего использовать GIN-индексы с расширением pg_trgm, которое позволяет эффективно искать по шаблонам в стиле %substring%.
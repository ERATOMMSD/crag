## Extending the main class (CRAG) and redefining `search_roads` method

The main class CRAG can be extended to introduce a new `search_roads` method. In its default definition, this method uses uniform random sampling for generating a single road geometry from a road configuration. This approach can be fast, but it may not be optimal if partitions used in generation of road geometries are too coarse. For coarse paritions, the fitness value associated with a road configuration may differ largely for different road geometries, since the sampled road geometries may vary a lot in shape. The method `search_roads` can be redefined to implement more advanced approaches. For example it can use repetitions to provide an average fitness value obtained by sampling multiple road geometries and evaluating them. Furthermore, one can use evolutionary computation techniques.

We note that there are trade-offs that one needs to consider when redefining the `search_roads` method. This method may be designed to spend more time for the search in a given road configuration. However, that may indirectly reduce the number of configurations that are explored (given the same budget).

We provide three example redefinitions of `search_roads` by extending `CRAG` class in three folders `roadsearch_default`, `roadsearch_repetition`, `roadsearch_1p1`.

### Default method (roadsearch_default folder)

This example illustrates the use of `CRAG` without modification to the original `search_roads` method.

### Repetition-based search method (roadsearch_repetition folder)

In this example, the `CRAG` class is extended so that the `search_roads` method conducts 5 repetitions of road geometry generation through sampling followed by evaluation. The best evaluation value is considered as the evaluation result for a given road configuration.

### 1 + 1 evolutionary search method (roadsearch_1p1 folder)

In this example, we use 1 + 1 evolutionary search algorithm with 5 generations. The search starts with a single individual road geometry generated from a road configuration. The mutation operator then takes a random road section and resamples the local geometry of only that section. If the new mutated road geometry achieves a better evaluation result, it replaces the current individual. This operation is repeated for 5 times.

### Trying different `search_roads` methods

[SBFT competition tool](https://github.com/sbft-cps-tool-competition/cps-tool-competition) is a dependency for the example code provided for different `search_roads` methods mentioned above. The following commands can be used to execute the competition tool with a time budget of 10800 seconds (3 hours) in generating and evaluating roads.

#### Default method (roadsearch_default folder)

``` sh
echo --best_ratio 0.1 --max_strength 4 --road_param_count 10 --road_param_value_count 4 --max_road_scalar 2 --min_road_scalar 0.6 | python [PATH TO cps-tool-competition\competition.py] --time-budget 10800 --executor beamng --beamng-home "[PATH TO THE BEAMNG FOLDER BeamNG.tech.v0.26.2.0]" --beamng-user "[PATH TO THE BEAMNG.DRIVE FOLDER Local\BeamNG.drive\0.26]" --map-size 200 --module-path "[PATH TO THE FOLDER roadsearch_examples]" --module-name roadsearch_default.cragdefault --class-name CRAGExample`
```

#### Repetition-based search method (roadsearch_repetition folder)

``` sh
echo --best_ratio 0.1 --max_strength 4 --road_param_count 10 --road_param_value_count 4 --max_road_scalar 2 --min_road_scalar 0.6 | python [PATH TO cps-tool-competition\competition.py] --time-budget 10800 --executor beamng --beamng-home "[PATH TO THE BEAMNG FOLDER BeamNG.tech.v0.26.2.0]" --beamng-user "[PATH TO THE BEAMNG.DRIVE FOLDER Local\BeamNG.drive\0.26]" --map-size 200 --module-path "[PATH TO THE FOLDER roadsearch_examples]" --module-name roadsearch_repetition.cragrepetition --class-name CRAGExample
```

#### 1 + 1 Evolutionary approach in search (roadsearch_1p1 folder)

``` sh
echo --best_ratio 0.1 --max_strength 4 --road_param_count 10 --road_param_value_count 4 --max_road_scalar 2 --min_road_scalar 0.6 | python [PATH TO cps-tool-competition\competition.py] --time-budget 10800 --executor beamng --beamng-home "[PATH TO THE BEAMNG FOLDER BeamNG.tech.v0.26.2.0]" --beamng-user "[PATH TO THE BEAMNG.DRIVE FOLDER Local\BeamNG.drive\0.26]" --map-size 200 --module-path "[PATH TO THE FOLDER roadsearch_examples]" --module-name roadsearch_1p1.crag1p1 --class-name CRAGExample
```

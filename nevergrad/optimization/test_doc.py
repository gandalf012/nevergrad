import warnings
import numpy as np
import nevergrad as ng
# pylint: disable=reimported,redefined-outer-name,unused-variable,unsubscriptable-object


def test_simplest_example() -> None:
    # DOC_SIMPLEST_0
    import nevergrad as ng

    def square(x):
        return sum((x - .5)**2)

    # optimization on x as an array of shape (2,)
    optimizer = ng.optimizers.OnePlusOne(parametrization=2, budget=100)
    recommendation = optimizer.minimize(square)  # best value
    print(recommendation.value)
    # >>> [0.49971112 0.5002944 ]
    # DOC_SIMPLEST_1
    np.testing.assert_array_almost_equal(recommendation.value, [0.5, 0.5], decimal=1)


def test_base_example() -> None:
    # DOC_BASE_0
    import nevergrad as ng

    def square(x, y=12):
        return sum((x - .5)**2) + abs(y)

    # optimization on x as an array of shape (2,)
    optimizer = ng.optimizers.OnePlusOne(parametrization=2, budget=100)
    recommendation = optimizer.minimize(square)  # best value
    print(recommendation.value)
    # >>> [0.49971112 0.5002944 ]
    # DOC_BASE_1
    instrum = ng.p.Instrumentation(ng.p.Array(shape=(2,)), y=ng.p.Scalar())
    optimizer = ng.optimizers.OnePlusOne(parametrization=instrum, budget=100)
    recommendation = optimizer.minimize(square)
    print(recommendation.value)
    # >>> [0.490, 0.546]
    # DOC_BASE_2
    from concurrent import futures
    optimizer = ng.optimizers.OnePlusOne(parametrization=instrum, budget=10, num_workers=2)

    with futures.ThreadPoolExecutor(max_workers=optimizer.num_workers) as executor:
        recommendation = optimizer.minimize(square, executor=executor, batch_mode=False)
    # DOC_BASE_3
    optimizer = ng.optimizers.OnePlusOne(parametrization=instrum, budget=10, num_workers=1)

    for _ in range(optimizer.budget):
        x = optimizer.ask()
        loss = square(*x.args, **x.kwargs)
        optimizer.tell(x, loss)

    recommendation = optimizer.provide_recommendation()
    # DOC_BASE_4


def test_print_all_optimizers() -> None:
    # DOC_OPT_REGISTRY_0
    import nevergrad as ng
    print(sorted(ng.optimizers.registry.keys()))
    # DOC_OPT_REGISTRY_1


def test_parametrization() -> None:
    # DOC_PARAM_0
    arg1 = ng.p.TransitionChoice(["a", "b"])
    arg2 = ng.p.Choice(["a", "c", "e"])
    value = ng.p.Scalar()

    instru = ng.p.Instrumentation(arg1, arg2, "blublu", value=value)
    print(instru.dimension)
    # >>> 5
    # DOC_PARAM_1

    def myfunction(arg1, arg2, arg3, value=3):
        print(arg1, arg2, arg3)
        return value**2

    optimizer = ng.optimizers.OnePlusOne(parametrization=instru, budget=100)
    recommendation = optimizer.minimize(myfunction)
    print(recommendation.value)
    # >>> (('b', 'e', 'blublu'), {'value': -0.00014738768964717153})
    # DOC_PARAM_2
    instru2 = instru.spawn_child().set_standardized_data([1, -80, -80, 80, 3])
    assert instru2.args == ('b', 'e', 'blublu')
    assert instru2.kwargs == {'value': 3}
    # DOC_PARAM_3


def test_doc_constrained_optimization() -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        # DOC_CONSTRAINED_0
        import nevergrad as ng

        def square(x):
            return sum((x - .5)**2)

        optimizer = ng.optimizers.OnePlusOne(parametrization=2, budget=100)
        # define a constraint on first variable of x:
        optimizer.parametrization.register_cheap_constraint(lambda x: x[0] >= 1)

        recommendation = optimizer.minimize(square)
        print(recommendation.value)
        # >>> [1.00037625, 0.50683314]
        # DOC_CONSTRAINED_1
    np.testing.assert_array_almost_equal(recommendation.value, [1, 0.5], decimal=1)

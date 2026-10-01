# Sentient cognitive libraries

The current package contains offline model-gateway validation only. It does not
own task state, grants, dispatch or cancellation; those remain Control Kernel
responsibilities. It is not connected to `/tasks` and does not load a provider.

See [model_gateway](model_gateway/README.md) for implemented boundaries and
remaining CP1 gates. The [canonical ownership document](../../../docs/architecture/canonical-ownership.md)
continues to define system responsibilities.

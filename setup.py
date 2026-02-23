from setuptools import setup, find_packages

setup(
    name='inventree-print-demand',
    version='0.1.0',
    description='InvenTree plugin to show aggregated 3D print demand across open orders',
    author='Micromelon',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['inventree'],
    entry_points={
        'inventree_plugins': [
            'PrintDemandPlugin = inventree_print_demand.plugin:PrintDemandPlugin',
        ],
    },
)

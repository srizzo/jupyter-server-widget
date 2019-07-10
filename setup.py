import setuptools

setuptools.setup(
    name="jupyter-server-widget",
    version='0.1.2',
    url='https://github.com/srizzo/jupyter-server-widget',
    author="Samuel Rizzo",
    author_email='rizzolabs@gmail.com',
    description="Jupyter Notebook %%magics and Widget to start and stop servers from a Cell",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license='MIT',
    install_requires=[
        'ipython',
        'jupyter'
    ],
    keywords=['ipython', 'jupyter'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
    ]
)

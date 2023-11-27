from setuptools import setup, find_packages

setup(
    name='rf_azure_sync',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'rf_azure_sync=rf_azure_sync.rf_azure_sync:rf_azure_sync',
        ],
    },
    author='Fábio Ribeiro dos Santos Quispe',
    author_email='fabiorisantos1981@gmail.com',
    description='Synchronization functionalities for Azure-related tasks.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fabiorisantosquispe/rf_azure_sync',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)

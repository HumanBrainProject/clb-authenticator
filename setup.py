from setuptools import setup, find_packages

requirements = [
    'oauthenticator>=0.9.0',
]

with open('README.md') as rm:
    long_description = rm.read()

setup(
    name='clb-authenticator',
    version='0.1.1',
    description='The Collaboratory Authenticator is based on the GenericOAuthenticator and adds user refreshing and roles.',
    long_description=long_description,
    author='Human Brain Project Collaboratory Team',
    author_email='support@humanbrainproject.eu',
    url='https://wiki.humanbrainproject.eu/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requirements
)

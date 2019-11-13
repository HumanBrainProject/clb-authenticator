from setuptools import setup, find_packages

requirements = [
    'oauthenticator>=0.9.0',
]

with open('README.md') as rm:
    long_description = rm.read()

setup(
    name='clb-oauthenticator',
    version='0.1.0',
    description='The collab Authenticator refreshes the user access tokens with the refresh token.',
    long_description=long_description,
    author='Human Brain Project Collaboratory Team',
    author_email='support@humanbrainproject.eu',
    url='https://wiki.humanbrainproject.eu/',
    packages=find_packages(),
    install_requires=requirements
)

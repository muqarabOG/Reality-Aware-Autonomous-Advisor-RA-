from setuptools import setup, find_packages

setup(
    name="ra3-advisor",
    version="1.0.0",
    author="Muqarab Nazir",
    author_author_email="", # Add email if desired
    description="Reality-Aware Autonomous Advisor: A Neuro-Symbolic AI Framework",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/muqarab-nazir/ra3_advisor", # Placeholder
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "numpy",
        "pandas",
        "opencv-python",
        "torch",
        "torchvision",
        "stable-baselines3",
        "river",
        "python-dotenv",
        "websockets",
        "ultralytics",
        "pyttsx3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.10',
)

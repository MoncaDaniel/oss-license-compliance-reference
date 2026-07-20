"""Shared pytest fixtures for the OSS compliance reference test suite."""

import pytest

from oss_compliance.models import ProductContext


@pytest.fixture
def internal_context():
    return ProductContext(product_name="Internal Tool", use_case="Internal")


@pytest.fixture
def saas_context():
    return ProductContext(product_name="Hosted App", use_case="SaaS")


@pytest.fixture
def distributed_context():
    return ProductContext(product_name="Shipped App", use_case="Distributed")


@pytest.fixture
def embedded_context():
    return ProductContext(product_name="Firmware", use_case="Embedded")


@pytest.fixture
def safety_critical_ai_context():
    return ProductContext(
        product_name="Signaling AI Module",
        use_case="Embedded",
        data_types=["Industrial/operational data"],
        target_markets=["EU"],
        is_safety_critical=True,
        has_ai=True,
    )

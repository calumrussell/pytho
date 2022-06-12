from django.db import models


class FactorReturns(models.Model):  # type: ignore
    factor: models.CharField = models.CharField(max_length=10, null=False, blank=False)
    ret: models.FloatField = models.FloatField(null=False, blank=False)
    name: models.CharField = models.CharField(max_length=50, null=False, blank=False)
    period: models.CharField = models.CharField(max_length=50, null=False, blank=False)
    period_name: models.CharField = models.CharField(max_length=100, primary_key=True)


class Coverage(models.Model):  # type: ignore
    country_name: models.CharField = models.CharField(
        max_length=20, null=False, blank=False
    )
    name: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    issuer: models.CharField = models.CharField(max_length=200, null=True)
    currency: models.CharField = models.CharField(max_length=5, null=True)
    ticker: models.CharField = models.CharField(max_length=10, null=True)
    security_type: models.CharField = models.CharField(
        max_length=10, null=False, blank=False
    )

    class Meta:
        unique_together = (
            ("country_name"),
            ("name"),
            ("currency"),
            ("issuer"),
        )


class SecFilingPaths(models.Model):  # type: ignore
    issuer_id: models.IntegerField = models.IntegerField(null=False, blank=False)
    form_id: models.SmallIntegerField = models.SmallIntegerField(
        null=False, blank=False
    )
    date: models.IntegerField = models.IntegerField(null=False, blank=False)
    path: models.CharField = models.CharField(max_length=20, null=False, blank=False)

    class Meta:
        unique_together = (
            ("issuer_id"),
            ("form_id"),
            ("date"),
        )


class SecFormId(models.Model):  # type: ignore
    form_id: models.AutoField = models.AutoField(
        null=False, blank=False, primary_key=True
    )
    form_name: models.CharField = models.CharField(
        max_length=20, null=False, blank=False
    )

    class Meta:
        unique_together = (("form_name"),)


class SecIssuerId(models.Model):  # type: ignore
    issuer_id: models.IntegerField = models.IntegerField(
        null=False, blank=False, primary_key=True
    )
    issuer_name: models.CharField = models.CharField(
        max_length=200, null=False, blank=False
    )


class SecThirteenFFiling(models.Model):  # type: ignore
    issuer_id: models.IntegerField = models.IntegerField(null=False, blank=False)
    filing_date: models.IntegerField = models.IntegerField(null=False, blank=False)
    period_date: models.IntegerField = models.IntegerField(null=False, blank=False)

    class Meta:
        unique_together = (
            ("issuer_id"),
            ("filing_date"),
        )


class SecThirteenFPosition(models.Model):  # type: ignore
    thirteenf_id: models.IntegerField = models.IntegerField(null=False, blank=False)
    shares: models.IntegerField = models.IntegerField(null=False, blank=False)
    value: models.IntegerField = models.IntegerField(null=False, blank=False)
    cusip: models.CharField = models.CharField(max_length=10, null=False, blank=False)

    class Meta:
        unique_together = (
            ("thirteenf_id"),
            ("cusip"),
        )

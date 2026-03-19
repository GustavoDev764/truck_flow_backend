import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.trucks.infrastructure.persistence.django_models import TruckModel

SEEDS: list[dict] = [
    {
        "license_plate": "ABC-1234",
        "brand": "Scania",
        "model_name": "FH 540",
        "manufacturing_year": 2020,
        "fipe_price": Decimal("450000.00"),
    },
    {
        "license_plate": "DEF-5678",
        "brand": "Volvo",
        "model_name": "FH 460",
        "manufacturing_year": 2019,
        "fipe_price": Decimal("420000.00"),
    },
    {
        "license_plate": "GHI-9012",
        "brand": "Mercedes-Benz",
        "model_name": "Actros 2651",
        "manufacturing_year": 2021,
        "fipe_price": Decimal("520000.00"),
    },
    {
        "license_plate": "JKL-3456",
        "brand": "Scania",
        "model_name": "R 450",
        "manufacturing_year": 2022,
        "fipe_price": Decimal("480000.00"),
    },
    {
        "license_plate": "MNO-7890",
        "brand": "Volvo",
        "model_name": "FH 540",
        "manufacturing_year": 2020,
        "fipe_price": Decimal("460000.00"),
    },
    {
        "license_plate": "PQR-2345",
        "brand": "Mercedes-Benz",
        "model_name": "Actros 2651",
        "manufacturing_year": 2023,
        "fipe_price": Decimal("550000.00"),
    },
    {
        "license_plate": "STU-6789",
        "brand": "MAN",
        "model_name": "TGX 28.440",
        "manufacturing_year": 2021,
        "fipe_price": Decimal("430000.00"),
    },
    {
        "license_plate": "VWX-0123",
        "brand": "Scania",
        "model_name": "R 500",
        "manufacturing_year": 2022,
        "fipe_price": Decimal("510000.00"),
    },
    {
        "license_plate": "YZA-4567",
        "brand": "Volvo",
        "model_name": "FH 460",
        "manufacturing_year": 2018,
        "fipe_price": Decimal("380000.00"),
    },
    {
        "license_plate": "BCD-8901",
        "brand": "Mercedes-Benz",
        "model_name": "Actros 2651",
        "manufacturing_year": 2020,
        "fipe_price": Decimal("500000.00"),
    },
    {
        "license_plate": "EFG-2345",
        "brand": "DAF",
        "model_name": "XF 460",
        "manufacturing_year": 2021,
        "fipe_price": Decimal("410000.00"),
    },
    {
        "license_plate": "HIJ-6789",
        "brand": "Scania",
        "model_name": "G 450",
        "manufacturing_year": 2019,
        "fipe_price": Decimal("440000.00"),
    },
    {
        "license_plate": "KLM-0123",
        "brand": "Volvo",
        "model_name": "FH 540",
        "manufacturing_year": 2022,
        "fipe_price": Decimal("470000.00"),
    },
    {
        "license_plate": "NOP-4567",
        "brand": "Iveco",
        "model_name": "Stralis 560",
        "manufacturing_year": 2020,
        "fipe_price": Decimal("390000.00"),
    },
    {
        "license_plate": "QRS-8901",
        "brand": "Mercedes-Benz",
        "model_name": "Actros 2651",
        "manufacturing_year": 2023,
        "fipe_price": Decimal("560000.00"),
    },
    {
        "license_plate": "TUV-2345",
        "brand": "Scania",
        "model_name": "R 450",
        "manufacturing_year": 2021,
        "fipe_price": Decimal("465000.00"),
    },
    {
        "license_plate": "WXY-6789",
        "brand": "Volvo",
        "model_name": "FH 460",
        "manufacturing_year": 2020,
        "fipe_price": Decimal("435000.00"),
    },
    {
        "license_plate": "ZAB-0123",
        "brand": "MAN",
        "model_name": "TGX 28.440",
        "manufacturing_year": 2022,
        "fipe_price": Decimal("445000.00"),
    },
    {
        "license_plate": "CDE-4567",
        "brand": "Mercedes-Benz",
        "model_name": "Actros 2651",
        "manufacturing_year": 2019,
        "fipe_price": Decimal("480000.00"),
    },
    {
        "license_plate": "FGH-8901",
        "brand": "Scania",
        "model_name": "FH 540",
        "manufacturing_year": 2023,
        "fipe_price": Decimal("530000.00"),
    },
    {
        "license_plate": "IJK-1234",
        "brand": "Volvo",
        "model_name": "FH 540",
        "manufacturing_year": 2022,
        "fipe_price": Decimal("475000.00"),
    },
    {
        "license_plate": "LMN-5678",
        "brand": "Mercedes-Benz",
        "model_name": "Actros 2651",
        "manufacturing_year": 2021,
        "fipe_price": Decimal("490000.00"),
    },
    {
        "license_plate": "OPQ-9012",
        "brand": "Scania",
        "model_name": "R 450",
        "manufacturing_year": 2023,
        "fipe_price": Decimal("525000.00"),
    },
    {
        "license_plate": "RST-3456",
        "brand": "MAN",
        "model_name": "TGX 28.440",
        "manufacturing_year": 2020,
        "fipe_price": Decimal("425000.00"),
    },
    {
        "license_plate": "UVW-7890",
        "brand": "DAF",
        "model_name": "XF 460",
        "manufacturing_year": 2022,
        "fipe_price": Decimal("435000.00"),
    },
    {
        "license_plate": "XYZ-2345",
        "brand": "Iveco",
        "model_name": "Stralis 560",
        "manufacturing_year": 2021,
        "fipe_price": Decimal("400000.00"),
    },
    {
        "license_plate": "AAA-6789",
        "brand": "Scania",
        "model_name": "G 450",
        "manufacturing_year": 2020,
        "fipe_price": Decimal("455000.00"),
    },
    {
        "license_plate": "BBB-0123",
        "brand": "Volvo",
        "model_name": "FH 460",
        "manufacturing_year": 2023,
        "fipe_price": Decimal("495000.00"),
    },
    {
        "license_plate": "CCC-4567",
        "brand": "Mercedes-Benz",
        "model_name": "Actros 2651",
        "manufacturing_year": 2022,
        "fipe_price": Decimal("540000.00"),
    },
    {
        "license_plate": "DDD-8901",
        "brand": "Scania",
        "model_name": "R 500",
        "manufacturing_year": 2021,
        "fipe_price": Decimal("505000.00"),
    },
    {
        "license_plate": "EEE-2345",
        "brand": "MAN",
        "model_name": "TGX 28.440",
        "manufacturing_year": 2023,
        "fipe_price": Decimal("455000.00"),
    },
]


class Command(BaseCommand):
    help = "Popular o banco com dados iniciais de caminhões (trucks)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Apaga todos os trucks antes de reinserir (idempotente via update_or_create sem essa flag).",
        )

    def handle(self, *args, **options):
        clear = bool(options.get("clear"))

        if clear:
            TruckModel.objects.all().delete()
            self.stdout.write(self.style.WARNING("Tabela trucks limpa (delete)."))

        now = timezone.now()
        days_back = 8 * 30
        n = len(SEEDS)
        dates = sorted([now - timedelta(days=random.randint(0, days_back)) for _ in range(n)])

        created = 0
        updated = 0

        for i, seed in enumerate(SEEDS):
            obj, is_created = TruckModel.objects.update_or_create(
                license_plate=seed["license_plate"],
                defaults={
                    "brand": seed["brand"],
                    "model_name": seed["model_name"],
                    "manufacturing_year": seed["manufacturing_year"],
                    "fipe_price": seed["fipe_price"],
                },
            )

            created_at = (
                dates[i] if i < len(dates) else now - timedelta(days=random.randint(0, days_back))
            )
            TruckModel.objects.filter(pk=obj.pk).update(created_at=created_at)

            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed concluida: created={created}, updated={updated} (datas nos últimos 8 meses)"
            )
        )

from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from pathlib import Path


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        models_path = Path(self.root_directory_path) / 'models.txt'

        if models_path.exists():
            with open(models_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        else:
            lines = []

        line_number = len(lines)

        with open(models_path, 'a', encoding='utf-8') as file:
            file.write(model.model_dump_json() + '\n')

        index_path = Path(self.root_directory_path) / 'models_index.txt'

        with open(index_path, 'a', encoding='utf-8') as file:
            file.write(str(model.id) + '|' + str(line_number) + '\n')
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        cars_path = Path(self.root_directory_path) / 'cars.txt'

        if cars_path.exists():
            with open(cars_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        else:
            lines = []

        line_number = len(lines)

        with open(cars_path, 'a', encoding='utf-8') as file:
            file.write(car.model_dump_json() + '\n')

        index_path = Path(self.root_directory_path) / 'cars_index.txt'

        with open(index_path, 'a', encoding='utf-8') as file:
            file.write(car.vin + '|' + str(line_number) + '\n')
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        sales_path = Path(self.root_directory_path) / 'sales.txt'

        if sales_path.exists():
            with open(sales_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        else:
            lines = []

        line_number = len(lines)

        with open(sales_path, 'a', encoding='utf-8') as file:
            file.write(sale.model_dump_json() + '\n')

        index_path = Path(self.root_directory_path) / 'sales_index.txt'

        with open(index_path, 'a', encoding='utf-8') as file:
            file.write(sale.car_vin + '|' + str(line_number) + '\n')

        cars_index_path = Path(self.root_directory_path) / 'cars_index.txt'

        with open(cars_index_path, 'r', encoding='utf-8') as file:
            index_lines = file.readlines()

        car_line_number = None

        for line in index_lines:
            vin, line_number_str = line.strip().split('|')

            if vin == sale.car_vin:
                car_line_number = int(line_number_str)
                break

        if car_line_number is None:
            raise ValueError("Car not found")

        cars_path = Path(self.root_directory_path) / 'cars.txt'

        with open(cars_path, 'r', encoding='utf-8') as file:
            car_lines = file.readlines()

        car_line = car_lines[car_line_number]
        car = Car.model_validate_json(car_line)
        car.status = CarStatus.sold

        car_lines[car_line_number] = car.model_dump_json() + '\n'

        with open(cars_path, 'w', encoding='utf-8') as file:
            file.writelines(car_lines)

        return car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        cars_path = Path(self.root_directory_path) / 'cars.txt'
        with open(cars_path, 'r', encoding='utf-8') as file:
            car_lines = file.readlines()

        cars = []

        for line in car_lines:
            car = Car.model_validate_json(line)
            if car.status == status:
                cars.append(car)

        return cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        cars_index_path = Path(self.root_directory_path) / 'cars_index.txt'

        with open(cars_index_path, 'r', encoding='utf-8') as file:
            index_lines = file.readlines()

        car_line_number = None

        for line in index_lines:
            file_vin, line_number_str = line.strip().split('|')

            if file_vin == vin:
                car_line_number = int(line_number_str)
                break

        if car_line_number is None:
            return None

        cars_path = Path(self.root_directory_path) / 'cars.txt'

        with open(cars_path, 'r', encoding='utf-8') as file:
            car_lines = file.readlines()

        car = Car.model_validate_json(car_lines[car_line_number])

        models_index_path = Path(self.root_directory_path) / 'models_index.txt'

        with open(models_index_path, 'r', encoding='utf-8') as file:
            model_index_lines = file.readlines()

        model_line_number = None

        for line in model_index_lines:
            model_id_str, line_number_str = line.strip().split('|')

            if int(model_id_str) == car.model:
                model_line_number = int(line_number_str)
                break
        if model_line_number is None:
            return None

        models_path = Path(self.root_directory_path) / 'models.txt'

        with open(models_path, 'r', encoding='utf-8') as file:
            model_lines = file.readlines()

        model = Model.model_validate_json(model_lines[model_line_number])

        sales_date = None
        sales_cost = None

        if car.status == CarStatus.sold:
            sales_path = Path(self.root_directory_path) / 'sales.txt'

            with open(sales_path, 'r', encoding='utf-8') as file:
                sale_lines = file.readlines()

            for line in sale_lines:
                sale = Sale.model_validate_json(line)

                if sale.car_vin == car.vin:
                    sales_date = sale.sales_date
                    sales_cost = sale.cost
                    break
        return CarFullInfo(
            vin=car.vin,
            car_model_name=model.name,
            car_model_brand=model.brand,
            price=car.price,
            date_start=car.date_start,
            status=car.status,
            sales_date=sales_date,
            sales_cost=sales_cost
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        cars_index_path = Path(self.root_directory_path) / 'cars_index.txt'

        with open(cars_index_path, 'r', encoding='utf-8') as file:
            index_lines = file.readlines()

        car_line_number = None

        for line in index_lines:
            file_vin, line_number_str = line.strip().split('|')

            if file_vin == vin:
                car_line_number = int(line_number_str)
                break

        if car_line_number is None:
            raise ValueError("Car not found")

        cars_path = Path(self.root_directory_path) / 'cars.txt'

        with open(cars_path, 'r', encoding='utf-8') as file:
            car_lines = file.readlines()

        car = Car.model_validate_json(car_lines[car_line_number])
        car.vin = new_vin

        car_lines[car_line_number] = car.model_dump_json() + '\n'

        with open(cars_path, 'w', encoding='utf-8') as file:
            file.writelines(car_lines)

        for i, line in enumerate(index_lines):
            file_vin, line_number_str = line.strip().split('|')

            if file_vin == vin:
                index_lines[i] = f'{new_vin}|{line_number_str}\n'
                break

        index_lines.sort(key=lambda x: x.split('|')[0])

        with open(cars_index_path, 'w', encoding='utf-8') as file:
            file.writelines(index_lines)

        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        sales_path = Path(self.root_directory_path) / 'sales.txt'

        with open(sales_path, 'r', encoding='utf-8') as file:
            sales_lines = file.readlines()
        sale_line_number = None
        sale_found = None

        for i, line in enumerate(sales_lines):
            sale = Sale.model_validate_json(line)

            if sale.sales_number == sales_number:
                sale_line_number = i
                sale_found = sale
                break

        if sale_line_number is None:
            raise ValueError("Sale not found")
        assert sale_found is not None
        car_vin = sale_found.car_vin

        del sales_lines[sale_line_number]

        with open(sales_path, 'w', encoding='utf-8') as file:
            file.writelines(sales_lines)

        cars_index_path = Path(self.root_directory_path) / 'cars_index.txt'

        with open(cars_index_path, 'r', encoding='utf-8') as file:
            index_lines = file.readlines()

        car_line_number = None

        for line in index_lines:
            file_vin, line_number_str = line.strip().split('|')

            if file_vin == car_vin:
                car_line_number = int(line_number_str)
                break

        if car_line_number is None:
            raise ValueError("Car not found")

        cars_path = Path(self.root_directory_path) / 'cars.txt'

        with open(cars_path, 'r', encoding='utf-8') as file:
            car_lines = file.readlines()

        car = Car.model_validate_json(car_lines[car_line_number])

        car.status = CarStatus.available

        car_lines[car_line_number] = car.model_dump_json() + '\n'

        with open(cars_path, 'w', encoding='utf-8') as file:
            file.writelines(car_lines)

        return car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        sales_by_model: dict[int, int] = {}

        sales_path = Path(self.root_directory_path) / 'sales.txt'

        with open(sales_path, 'r', encoding='utf-8') as file:
            sales_lines = file.readlines()
        for line in sales_lines:
            sale = Sale.model_validate_json(line)

            cars_index_path = Path(self.root_directory_path) / 'cars_index.txt'
            with open(cars_index_path, 'r', encoding='utf-8') as file:
                index_lines = file.readlines()
            car_line_number = None

            for index_line in index_lines:
                file_vin, line_number_str = index_line.strip().split('|')

                if file_vin == sale.car_vin:
                    car_line_number = int(line_number_str)
                    break

            if car_line_number is None:
                continue

            cars_path = Path(self.root_directory_path) / 'cars.txt'

            with open(cars_path, 'r', encoding='utf-8') as file:
                car_lines = file.readlines()

            car = Car.model_validate_json(car_lines[car_line_number])

            model_id = car.model

            if model_id in sales_by_model:
                sales_by_model[model_id] += 1
            else:
                sales_by_model[model_id] = 1

        sorted_models = sorted(
            sales_by_model.items(),
            key=lambda x: x[1],
            reverse=True
        )
        top_models = sorted_models[:3]
        result = []

        for model_id, sales_count in top_models:
            models_index_path = (
                Path(self.root_directory_path)
                / 'models_index.txt'
            )

            with open(models_index_path, 'r', encoding='utf-8') as file:
                model_index_lines = file.readlines()

            model_line_number = None

            for line in model_index_lines:
                model_id_str, line_number_str = line.strip().split('|')

                if int(model_id_str) == model_id:
                    model_line_number = int(line_number_str)
                    break

            if model_line_number is None:
                continue
            models_path = Path(self.root_directory_path) / 'models.txt'

            with open(models_path, 'r', encoding='utf-8') as file:
                model_lines = file.readlines()

            model = Model.model_validate_json(model_lines[model_line_number])

            result.append(
                ModelSaleStats(
                    car_model_name=model.name,
                    brand=model.brand,
                    sales_number=sales_count
                )
            )
        return result

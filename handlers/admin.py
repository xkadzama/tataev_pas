from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.engine import AsyncSessionLocal
from database.models import Category
from keyboards.button_template import admin_kb, build_cancel_kb  # добавить build_cansel_kb функции
from keyboards.keyboard_builder import make_row_inline_keyboards
from states.states import NewCategoryStates

router = Router()


@router.message(Command("admin_panel"))
async def admin_panel(message: Message):
    inline_kb = make_row_inline_keyboards(admin_kb)
    await message.answer(
        "👨‍💼 <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        reply_markup=inline_kb
    )


@router.callback_query(F.data == "new_category_furniture")
async def start_add_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NewCategoryStates.name_category)

    cancel_kb = make_row_inline_keyboards(build_cancel_kb)
    await callback.message.edit_text(
        "📝 <b>Добавление новой категории</b>\n\n"
        "Введите <b>название</b> новой категории:\n"
        "Пример: Детская мебель, Офисная мебель и т.д.",
        reply_markup=cancel_kb
    )
    await callback.answer()


@router.message(NewCategoryStates.name_category)
async def process_category_name(message: Message, state: FSMContext):
    category_name = message.text.strip()
    print(category_name)
    if len(category_name) < 2:
        await message.answer(
            "❌ Название слишком короткое. Минимум 2 символа.\n"
            "Попробуйте снова:"
        )
        return

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        query = select(Category).where(Category.name == category_name)
        result = await session.execute(query)
        print(result)
        existing = result.scalar_one_or_none()

        if existing:
            await message.answer(
                f"❌ Категория <b>'{category_name}'</b> уже существует!\n"
                "Введите другое название:"
            )
            return

    await state.update_data(category_name=category_name)
    await state.set_state(NewCategoryStates.type_category)

    type_kb = make_row_inline_keyboards([
        ("Спальная мебель", "type_bedroom"),
        ("Кухонная мебель", "type_kitchen"),
        ("Мягкая мебель", "type_soft"),
        ("Столы и стулья", "type_tables"),
        ("Шкафы", "type_wardrobes"),
        ("Другое", "type_other"),
    ])

    await message.answer(
        "🏷️ <b>Выберите тип мебели</b>\n\n"
        "К какому типу тотносится эта категория?",
        reply_markup=type_kb
    )


@router.callback_query(F.data.startswith("type_"), NewCategoryStates.type_category)
async def process_category_type(callback: CallbackQuery, state: FSMContext):
    type_map = {
        "type_bedroom": "Спальная мебель",
        "type_kitchen": "Кухонная мебель",
        "type_soft": "Мягкая мебель",
        "type_tables": "Столы и стулья",
        "type_wardrobes": "Шкафы",
        "type_other": "Другое"
    }

    category_type = type_map.get(callback.data, "Другое")
    await state.update_data(category_type=category_type)
    await state.set_state(NewCategoryStates.description_category)

    cancel_kb = make_row_inline_keyboards(build_cancel_kb)
    await callback.message.edit_text(
        "📝 <b>Добавление описания</b>\n\n"
        "Введите <b>описание</b> категории (или нажмите 'Пропустить'):\n\n"
        "Пример: Мебель для спальни, включает кровати, шкафы, тумбы",
        reply_markup=cancel_kb
    )
    await callback.answer()


@router.message(NewCategoryStates.description_category)
async def process_category_description(message: Message, state: FSMContext):
    description = message.text.strip()

    if description.lower() in ["пропустить", "skip", "-", "—"]:
        description = None

    await state.update_data(category_description=description)

    data = await state.get_data()
    category_name = data.get("category_name")
    category_type = data.get("category_type")
    category_description = data.get("category_description")

    try:
        async with AsyncSessionLocal() as session:
            new_category = Category(
                name=category_name,
                type=category_type,
                description=category_description,
            )
            session.add(new_category)
            await session.commit()

            await message.answer(
                f"✅ <b>Категория успешно добавлена!</b>\n\n"
                f"📌 Название: {category_name}\n"
                f"🏷️ Тип: {category_type}\n"
                f"📝 Описание: {category_description or 'Не указано'}"
            )

            inline_kb = make_row_inline_keyboards(admin_kb)
            await message.answer(
                "👨‍💼 <b>Админ-панель</b>\n\n"
                "Выберите действие:",
                reply_markup=inline_kb
            )

    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {str(e)}")

    finally:
        await state.clear()


@router.callback_query(F.data == "cancel_category")
async def cancel_add_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    inline_kb = make_row_inline_keyboards(admin_kb)
    await callback.message.edit_text(
        "❌ Добавление категории отменено.\n\n"
        "👨‍💼 <b>Админ-панель</b>",
        reply_markup=inline_kb
    )
    await callback.answer()

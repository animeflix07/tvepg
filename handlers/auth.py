import logging
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import OWNER_ID
from database.db import Database
from utils.jiotv_wrapper import JioTVWrapper

logger = logging.getLogger(__name__)
router = Router()

class LoginStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_otp = State()

@router.message(Command("login"))
async def login_command(message: types.Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Only owner can login.")
        return

    await message.answer("📱 Please enter your Jio phone number (10 digits):")
    await state.set_state(LoginStates.waiting_for_phone)

@router.message(LoginStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.isdigit() or len(phone) != 10:
        await message.answer("❌ Invalid phone number. Please enter 10 digits:")
        return

    try:
        jio = JioTVWrapper()
        result = await jio.request_otp(phone)

        if result.get("status") == "success":
            await state.update_data(phone=phone)
            await message.answer("📧 OTP sent to your registered email. Please enter the OTP:")
            await state.set_state(LoginStates.waiting_for_otp)
        else:
            await message.answer(f"❌ Failed to send OTP: {result.get('message')}")
    except Exception as e:
        logger.error(f"OTP request failed: {e}")
        await message.answer(f"❌ Error: {str(e)}")

@router.message(LoginStates.waiting_for_otp)
async def process_otp(message: types.Message, state: FSMContext):
    otp = message.text.strip()
    data = await state.get_data()
    phone = data.get("phone")

    try:
        jio = JioTVWrapper()
        result = await jio.verify_otp(phone, otp)

        if result.get("status") == "success":
            token = result.get("token")
            token_expiry = result.get("token_expiry")

            # Save credentials
            await Database.update_user(
                message.from_user.id,
                {
                    "jio_phone": phone,
                    "jio_token": token,
                    "token_expiry": token_expiry
                }
            )

            await message.answer("✅ Login successful! Token will auto-refresh.")
            await state.clear()
        else:
            await message.answer(f"❌ OTP verification failed: {result.get('message')}")
    except Exception as e:
        logger.error(f"OTP verification failed: {e}")
        await message.answer(f"❌ Error: {str(e)}")

@router.message(Command("premium"))
async def premium_status(message: types.Message):
    user = await Database.get_user(message.from_user.id)

    if not user:
        await message.answer("❌ User not found.")
        return

    if user.get("is_premium"):
        expiry = user.get("premium_expiry")
        if expiry:
            await message.answer(f"✅ Premium member until {expiry.strftime('%Y-%m-%d')}")
        else:
            await message.answer("✅ Premium member (Permanent)")
    else:
        await message.answer("❌ Not a premium member. Contact @II_Madara_II for access.")

import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas
import os
import resend

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class InviteService:
    def __init__(self, db: Session):
        self.db = db
        print("RESEND KEY:", os.getenv("RESEND_API_KEY"))
        resend.api_key = os.getenv("RESEND_API_KEY")

    def create_invite(self, invite_data: schemas.TeacherInviteCreate) -> models.TeacherInvite:
        # Check if teacher exists
        teacher = self.db.query(models.Teacher).filter(models.Teacher.id == invite_data.teacher_id).first()
        if not teacher:
            raise ValueError(f"Teacher with id {invite_data.teacher_id} not found")

        # Check if teacher already has auth
        existing_auth = self.db.query(models.TeacherAuth).filter(models.TeacherAuth.teacher_id == invite_data.teacher_id).first()
        if existing_auth:
            raise ValueError(f"Teacher {invite_data.teacher_id} already has authentication setup")

        # Generate secure token
        token = str(uuid.uuid4())
        invite_id = str(uuid.uuid4())

        # Create invite with 24 hour expiry
        expires_at = datetime.utcnow() + timedelta(hours=24)

        invite = models.TeacherInvite(
            id=invite_id,
            teacher_id=invite_data.teacher_id,
            email=invite_data.email,
            token=token,
            expires_at=expires_at
        )

        self.db.add(invite)
        self.db.commit()
        self.db.refresh(invite)

        # Send email
        self._send_invite_email(invite, teacher)

        return invite

    def activate_account(self, activation_data: schemas.TeacherActivation) -> models.TeacherAuth:
        # Find invite by token
        invite = self.db.query(models.TeacherInvite).filter(
            models.TeacherInvite.token == activation_data.token,
            models.TeacherInvite.is_used == False
        ).first()

        if not invite:
            raise ValueError("Invalid or expired invitation token")

        if datetime.utcnow() > invite.expires_at:
            raise ValueError("Invitation token has expired")

        # Check if username is unique
        existing_user = self.db.query(models.User).filter(models.User.username == activation_data.username).first()
        existing_teacher_auth = self.db.query(models.TeacherAuth).filter(models.TeacherAuth.username == activation_data.username).first()
        if existing_user or existing_teacher_auth:
            raise ValueError("Username already taken")

        # Create TeacherAuth
        hashed_password = pwd_context.hash(activation_data.password)
        teacher_auth = models.TeacherAuth(
            teacher_id=invite.teacher_id,
            username=activation_data.username,
            hashed_password=hashed_password
        )

        self.db.add(teacher_auth)

        # Mark invite as used
        invite.is_used = True

        self.db.commit()
        self.db.refresh(teacher_auth)

        return teacher_auth

    def _send_invite_email(self, invite: models.TeacherInvite, teacher: models.Teacher):
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        activation_link = f"{frontend_url}/activate?token={invite.token}"

        html_content = f"""
        <h1>Teacher Account Invitation</h1>
        <p>Dear {teacher.name},</p>
        <p>You have been invited to create an account for the DU Examination Remuneration System.</p>
        <p>Please click the link below to activate your account:</p>
        <a href="{activation_link}">Activate Account</a>
        <p>This link will expire in 24 hours.</p>
        <p>If you did not request this invitation, please ignore this email.</p>
        """

        try:
            resend.Emails.send({
                "from": "onboarding@resend.dev",  # Replace with your verified domain
                "to": invite.email,
                "subject": "DU Examination System - Account Activation",
                "html": html_content,
            })
        except Exception as e:
            print(f"Failed to send email: {e}")
            # In production, you might want to log this or handle it differently
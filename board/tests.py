from django.test import TestCase
from django.urls import reverse

from accounts.models import Tag, User

from .models import Rant


class BoardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.mood = Tag.objects.create(name="Stressed", kind=Tag.MOOD)
        cls.interest = Tag.objects.create(name="Gaming", kind=Tag.INTEREST)
        cls.alice = User.objects.create_user("alice", "alice@example.com", "pass12345!")
        cls.bob = User.objects.create_user("bob", "bob@example.com", "pass12345!")
        cls.mod = User.objects.create_user(
            "mod", "mod@example.com", "pass12345!", role=User.MODERATOR
        )

    def post_rant(self, **kw):
        data = {"title": "", "mood": self.mood.pk, "content": "This week was really rough."}
        data.update(kw)
        return self.client.post(reverse("board:create"), data)

    # --- access ---
    def test_logged_out_redirected_to_login(self):
        for name, args in [("board:list", []), ("board:create", []), ("board:mine", []),
                           ("board:detail", [1]), ("board:edit", [1]), ("board:delete", [1])]:
            r = self.client.get(reverse(name, args=args))
            self.assertEqual(r.status_code, 302, name)
            self.assertIn("/login/", r["Location"])

    # --- create + validation ---
    def test_create_saves_with_author(self):
        self.client.force_login(self.alice)
        r = self.post_rant(is_anonymous="on")
        rant = Rant.objects.get()
        self.assertRedirects(r, reverse("board:detail", args=[rant.pk]))
        self.assertEqual(rant.author, self.alice)
        self.assertTrue(rant.is_anonymous)

    def test_too_short_and_blank_rejected(self):
        self.client.force_login(self.alice)
        for text in ["short", "          ", ""]:
            r = self.post_rant(content=text)
            self.assertEqual(r.status_code, 200)
        self.assertEqual(Rant.objects.count(), 0)

    def test_too_long_rejected(self):
        self.client.force_login(self.alice)
        self.post_rant(content="x" * 1001)
        self.assertEqual(Rant.objects.count(), 0)

    def test_interest_tag_not_allowed_as_mood(self):
        self.client.force_login(self.alice)
        self.post_rant(mood=self.interest.pk)
        self.assertEqual(Rant.objects.count(), 0)

    def test_daily_limit(self):
        self.client.force_login(self.alice)
        for _ in range(10):
            self.post_rant()
        r = self.post_rant()
        self.assertEqual(Rant.objects.count(), 10)
        self.assertContains(r, "up to 10 rants per day")

    # --- anonymity ---
    def test_anonymous_hidden_from_members_visible_to_moderator(self):
        Rant.objects.create(author=self.alice, content="a secret rant here", is_anonymous=True)
        self.client.force_login(self.bob)
        page = self.client.get(reverse("board:list"))
        self.assertContains(page, "Anonymous")
        self.assertNotContains(page, "alice")
        self.client.force_login(self.mod)
        page = self.client.get(reverse("board:list"))
        self.assertContains(page, "posted by alice")

    # --- update / delete permissions ---
    def test_only_author_can_edit(self):
        rant = Rant.objects.create(author=self.alice, content="original content here")
        url = reverse("board:edit", args=[rant.pk])
        self.client.force_login(self.bob)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(url, {"content": "hacked content here"}).status_code, 403)
        self.client.force_login(self.mod)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.force_login(self.alice)
        r = self.client.post(url, {"title": "", "content": "updated content here"})
        self.assertEqual(r.status_code, 302)
        rant.refresh_from_db()
        self.assertEqual(rant.content, "updated content here")

    def test_delete_permissions(self):
        rant = Rant.objects.create(author=self.alice, content="to be deleted maybe")
        url = reverse("board:delete", args=[rant.pk])
        self.client.force_login(self.bob)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertEqual(Rant.objects.count(), 1)
        self.client.force_login(self.mod)  # moderators may delete any rant
        self.client.post(url)
        self.assertEqual(Rant.objects.count(), 0)

    def test_author_can_delete_own(self):
        rant = Rant.objects.create(author=self.alice, content="to be deleted maybe")
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(reverse("board:delete", args=[rant.pk])).status_code, 200)
        self.client.post(reverse("board:delete", args=[rant.pk]))
        self.assertEqual(Rant.objects.count(), 0)

    # --- dashboards / integration ---
    def test_dashboards_show_feature(self):
        Rant.objects.create(author=self.alice, content="dashboard visible rant")
        self.client.force_login(self.alice)
        self.assertContains(self.client.get(reverse("member_dashboard")), "dashboard visible rant")
        self.client.force_login(self.mod)
        self.assertContains(self.client.get(reverse("moderator_dashboard")), "Total rants")

    def test_role_dashboards_still_protected(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(reverse("moderator_dashboard")).status_code, 403)
        self.client.force_login(self.mod)
        self.assertEqual(self.client.get(reverse("member_dashboard")).status_code, 403)

    def test_profile_lists_past_posts(self):
        Rant.objects.create(author=self.alice, content="my own past post here")
        self.client.force_login(self.alice)
        self.assertContains(self.client.get(reverse("profile")), "my own past post here")

    def test_register_login_standard_features(self):
        r = self.client.post(reverse("register"), {
            "username": "carol", "first_name": "C", "last_name": "D",
            "email": "carol@example.com", "password1": "Str0ngPass!word", "password2": "Str0ngPass!word"})
        self.assertRedirects(r, reverse("login"))
        self.assertNotEqual(User.objects.get(username="carol").password, "Str0ngPass!word")
        dup = self.client.post(reverse("register"), {
            "username": "carol2", "first_name": "C", "last_name": "D",
            "email": "CAROL@example.com", "password1": "Str0ngPass!word", "password2": "Str0ngPass!word"})
        self.assertContains(dup, "already exists")

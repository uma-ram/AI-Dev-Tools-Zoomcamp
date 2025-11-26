from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import Todo

class TodoModelTest(TestCase):
    
    def test_create_todo_with_all_fields(self):
        """Test creating a TODO with all fields"""
        todo = Todo.objects.create(
            title="Test TODO",
            description="Test description",
            due_date=date.today() + timedelta(days=7),
            resolved=False
        )
        self.assertEqual(todo.title, "Test TODO")
        self.assertEqual(todo.description, "Test description")
        self.assertFalse(todo.resolved)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)
    
    def test_create_todo_minimal_fields(self):
        """Test creating a TODO with only required fields"""
        todo = Todo.objects.create(title="Minimal TODO")
        self.assertEqual(todo.title, "Minimal TODO")
        self.assertEqual(todo.description, "")
        self.assertIsNone(todo.due_date)
        self.assertFalse(todo.resolved)
    
    def test_todo_string_representation(self):
        """Test the string representation of a TODO"""
        todo = Todo.objects.create(title="String Test")
        self.assertEqual(str(todo), "String Test")


class TodoViewTest(TestCase):
    
    def setUp(self):
        """Set up test client and create test TODOs"""
        self.client = Client()
        self.todo1 = Todo.objects.create(
            title="Active TODO",
            description="This is active",
            due_date=date.today() + timedelta(days=3),
            resolved=False
        )
        self.todo2 = Todo.objects.create(
            title="Completed TODO",
            description="This is done",
            resolved=True
        )
    
    def test_todo_list_view(self):
        """Test that the list view displays TODOs"""
        response = self.client.get(reverse('todo-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active TODO")
        self.assertContains(response, "Completed TODO")
        self.assertTemplateUsed(response, 'todos/todo_list.html')
    
    def test_todo_create_view_get(self):
        """Test GET request to create view"""
        response = self.client.get(reverse('todo-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_form.html')
    
    def test_todo_create_view_post(self):
        """Test POST request to create a new TODO"""
        data = {
            'title': 'New TODO',
            'description': 'New description',
            'due_date': date.today() + timedelta(days=5)
        }
        response = self.client.post(reverse('todo-create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Todo.objects.filter(title='New TODO').exists())
    
    def test_todo_update_view(self):
        """Test updating an existing TODO"""
        data = {
            'title': 'Updated TODO',
            'description': 'Updated description',
            'due_date': date.today() + timedelta(days=10),
            'resolved': True
        }
        response = self.client.post(
            reverse('todo-update', kwargs={'pk': self.todo1.pk}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, 'Updated TODO')
        self.assertTrue(self.todo1.resolved)
    
    def test_todo_delete_view(self):
        """Test deleting a TODO"""
        response = self.client.post(
            reverse('todo-delete', kwargs={'pk': self.todo1.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(pk=self.todo1.pk).exists())
    
    def test_toggle_resolved(self):
        """Test toggling the resolved status"""
        # Initially False
        self.assertFalse(self.todo1.resolved)
        
        # Toggle to True
        response = self.client.get(
            reverse('todo-toggle', kwargs={'pk': self.todo1.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.todo1.refresh_from_db()
        self.assertTrue(self.todo1.resolved)
        
        # Toggle back to False
        response = self.client.get(
            reverse('todo-toggle', kwargs={'pk': self.todo1.pk})
        )
        self.todo1.refresh_from_db()
        self.assertFalse(self.todo1.resolved)
    
    def test_create_todo_without_required_fields(self):
        """Test that creating a TODO without title fails"""
        data = {
            'description': 'No title',
        }
        response = self.client.post(reverse('todo-create'), data)
        self.assertEqual(response.status_code, 200)  # Returns to form with errors
        self.assertFalse(Todo.objects.filter(description='No title').exists())
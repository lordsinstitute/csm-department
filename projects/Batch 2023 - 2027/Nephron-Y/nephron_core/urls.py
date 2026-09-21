from django.contrib import admin
from django.urls import path
from diagnosis import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Portals
    path('choice/', views.choice_view, name='choice'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('doctor/', views.doctor_view, name='doctor_dashboard'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics_view'),
    
    # Shop & Cart URLs
    path('shop/', views.shop_view, name='shop'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    
    # === MISSING CART VIEW ===
    path('cart/', views.cart_view, name='cart'), 
    
    # === REMOVE CART ITEM URL ===
    path('remove-item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    # === DELETE RECORD ROUTE ===
    path('delete/<int:record_id>/', views.delete_record, name='delete_record'),
    path('feedback/<int:record_id>/', views.submit_feedback, name='submit_feedback'),
    path('delete-patient/<int:record_id>/', views.delete_patient, name='delete_patient'),
    path('emergency-sos/', views.emergency_sos, name='emergency_sos'),
]
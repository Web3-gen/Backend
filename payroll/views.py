from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Sum
from datetime import datetime
from .models import PayRoll
from .serializers import PayRollSerializer
from user_profile.models import RecipientProfile, OrganizationProfile

class PayRollViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling PayRoll operations.
    Provides different views based on user type (organization or recipient)
    """
    serializer_class = PayRollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter queryset based on user type:
        - Organizations see all their payrolls
        - Recipients see only their payrolls
        """
        user = self.request.user
        
        try:
            # Check if user is an organization
            org_profile = OrganizationProfile.objects.get(user=user)
            return PayRoll.objects.filter(organization=org_profile)
        except OrganizationProfile.DoesNotExist:
            try:
                # Check if user is a recipient
                recipient_profile = RecipientProfile.objects.get(user=user)
                return PayRoll.objects.filter(recipient=recipient_profile)
            except RecipientProfile.DoesNotExist:
                return PayRoll.objects.none()

    def perform_create(self, serializer):
        """
        Ensure organization can only create payrolls for their own account
        """
        try:
            org_profile = OrganizationProfile.objects.get(user=self.request.user)
            serializer.save(organization=org_profile)
        except OrganizationProfile.DoesNotExist:
            raise PermissionError("Only organizations can create payroll entries")

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get summary of payrolls including total amount paid and pending
        """
        queryset = self.get_queryset()
        total_paid = queryset.filter(is_paid=True).aggregate(Sum('amount'))
        total_pending = queryset.filter(is_paid=False).aggregate(Sum('amount'))
        
        return Response({
            'total_paid': total_paid['amount__sum'] or 0,
            'total_pending': total_pending['amount__sum'] or 0,
            'total_entries': queryset.count()
        })

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """
        Get monthly breakdown of payrolls
        """
        year = request.query_params.get('year', datetime.now().year)
        queryset = self.get_queryset().filter(date__year=year)
        
        monthly_data = {}
        for month in range(1, 13):
            monthly_amount = queryset.filter(
                date__month=month,
                is_paid=True
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            monthly_data[month] = monthly_amount

        return Response(monthly_data)

    def update(self, request, *args, **kwargs):
        """
        Update payroll entry with additional validation
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Prevent updating certain fields after payment
        if instance.is_paid and not request.user.is_staff:
            return Response(
                {"detail": "Paid payrolls cannot be modified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """
        Mark a payroll entry as paid
        """
        payroll = self.get_object()
        if payroll.is_paid:
            return Response(
                {"detail": "Payroll already marked as paid"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payroll.is_paid = True
        payroll.paid_at = datetime.now()
        payroll.status = 'completed'
        payroll.save()

        serializer = self.get_serializer(payroll)
        return Response(serializer.data)

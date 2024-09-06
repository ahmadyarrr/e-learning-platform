from typing import Any
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class OrderField(models.PositiveIntegerField):
    # self.attname, model_instance, self.model
    def __init__(self,for_fields=None, *args: Any, **kwargs: Any) -> None:
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    # overriding
    def pre_save(self, model_instance: models.Model,add: bool) -> Any:
        if getattr(model_instance,self.attname) is None:
            # if no value of ordering exists
            try:
                qs = self.model.objects.all()

                if self.for_fields:
                    filter_q = { # e.g. if module-6 is from course-3 --> then find all other modules which are from course 3
                        field: getattr(model_instance,field) \
                            for field in self.for_fields 
                    }
                    qs = qs.filter(**filter_q)

                last = qs.last()
                value = last.order + 1
            except (ObjectDoesNotExist, AttributeError):
                value = 0
            setattr(model_instance,self.attname,value)            
            return value
        else:
            return super().pre_save(model_instance,add)






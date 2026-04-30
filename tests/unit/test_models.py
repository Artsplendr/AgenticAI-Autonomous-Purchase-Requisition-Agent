from models.requisition import ParsedRequisition, Item


def test_requisition_model_builds():
    model = ParsedRequisition(items=[Item(name='laptop', quantity=2)])
    assert model.items[0].name == 'laptop'

from Backend import db_helper

def test_fetch_db():
    expnse = db_helper.fecth_day_data('2024-08-15')

    assert len(expnse)>0
    assert expnse[0]["amount"]==10.0
    assert expnse[0]["category"]=="Shopping"
    assert expnse[0]["notes"]=="Bought potatoes"
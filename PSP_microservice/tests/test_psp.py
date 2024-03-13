import pytest
from main import app, get_prediction, get_alphafold_sequence, predict_endpoint, read_task
from src.endpoints import predict_protein_structure, async_predict, get_task_status  # noqa: E501
from fastapi.testclient import TestClient
import sys

sys.path.append("..")
client = TestClient(app)


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'pyamqp://guest@localhost:5672//',
        'result_backend': 'rpc://',
    }


def test_default_response():
    response = client.get('/')
    assert response.status_code == 200


def test_get_prediction_P00520():
    test_qualifier = "P00520"
    test_entryID = "AF-P00520-F1"
    test_get_prediction_res = get_prediction(test_qualifier)
    test_get_prediction_res = test_get_prediction_res['aphafold_raw_data'][0]['entryId']  # noqa: E501
    assert test_get_prediction_res == test_entryID


def test_get_prediction_P00420():
    test_qualifier = "P00420"
    test_entryID = "AF-P00420-F1"
    test_get_prediction_res = get_prediction(test_qualifier)
    test_get_prediction_res = test_get_prediction_res['aphafold_raw_data'][0]['entryId']  # noqa: E501
    assert test_get_prediction_res == test_entryID


def test_get_alphafold_sequence_P00520():
    test_qualifier = "P00520"
    test_seq = "MLEICLKLVGCKSKKGLSSSSSCYLEEALQRPVASDFEPQGLSEAARWNSKENLLAGPSENDPNLFVALYDFVASGDNTLSITKGEKLRVLGYNHNGEWCEAQTKNGQGWVPSNYITPVNSLEKHSWYHGPVSRNAAEYLLSSGINGSFLVRESESSPGQRSISLRYEGRVYHYRINTASDGKLYVSSESRFNTLAELVHHHSTVADGLITTLHYPAPKRNKPTIYGVSPNYDKWEMERTDITMKHKLGGGQYGEVYEGVWKKYSLTVAVKTLKEDTMEVEEFLKEAAVMKEIKHPNLVQLLGVCTREPPFYIITEFMTYGNLLDYLRECNRQEVSAVVLLYMATQISSAMEYLEKKNFIHRDLAARNCLVGENHLVKVADFGLSRLMTGDTYTAHAGAKFPIKWTAPESLAYNKFSIKSDVWAFGVLLWEIATYGMSPYPGIDLSQVYELLEKDYRMERPEGCPEKVYELMRACWQWNPSDRPSFAEIHQAFETMFQESSISDEVEKELGKRGTRGGAGSMLQAPELPTKTRTCRRAAEQKDAPDTPELLHTKGLGESDALDSEPAVSPLLPRKERGPPDGSLNEDERLLPRDRKTNLFSALIKKKKKMAPTPPKRSSSFREMDGQPDRRGASEDDSRELCNGPPALTSDAAEPTKSPKASNGAGVPNGAFREPGNSGFRSPHMWKKSSTLTGSRLAAAEEESGMSSSKRFLRSCSASCMPHGARDTEWRSVTLPRDLPSAGKQFDSSTFGGHKSEKPALPRKRTSESRSEQVAKSTAMPPPRLVKKNEEAAEEGFKDTESSPGSSPPSLTPKLLRRQVTASPSSGLSHKEEATKGSASGMGTPATAEPAPPSNKVGLSKASSEEMRVRRHKHSSESPGRDKGRLAKLKPAPPPPPACTGKAGKPAQSPSQEAGEAGGPTKTKCTSLAMDAVNTDPTKAGPPGEGLRKPVPPSVPKPQSTAKPPGTPTSPVSTPSTAPAPSPLAGDQQPSSAAFIPLISTRVSLRKTRQPPERIASGTITKGVVLDSTEALCLAISRNSEQMASHSAVLEAGKNLYTFCVSYVDSIQQMRNKFAFREAINKLESNLRELQICPATASSGPAATQDFSKLLSSVKEISDIVRR"  # noqa: E501
    test_get_sequence_res = get_alphafold_sequence(test_qualifier)
    assert test_seq == test_get_sequence_res["Sequence"]


def test_get_alphafold_sequence_P00420():
    test_qualifier = "P00420"
    test_seq = "MTHLERSRHQQHPFHMVMPSPWPIVVSFALLSLALSTALTMHGYIGNMNMVYLALFVLLTSSILWFRDIVAEATYLGDHTMAVRKGINLGFLMFVLSEVLIFAGLFWAYFHSAMSPDVTLGACWPPVGIEAVQPTELPLLNTIILLSSGATVTYSHHALIAGNRNKALSGLLITFWLIVIFVTCQYIEYTNAAFTISDGVYGSVFYAGTGLHFLHMVMLAAMLGVNYWRMRNYHLTAGHHVGYETTIIYTHVLDVIWLFLYVVFYWWGV"  # noqa: E501
    test_get_sequence_res = get_alphafold_sequence(test_qualifier)
    assert test_seq == test_get_sequence_res["Sequence"]


def test_get_prediction_P00722():
    test_qualifier = "P00722"
    test_entryID = "AF-P00722-F1"
    test_get_prediction_res = get_prediction(test_qualifier)
    test_get_prediction_res = test_get_prediction_res['aphafold_raw_data'][0]['entryId']  # noqa: E501
    assert test_get_prediction_res == test_entryID


def test_get_alphafold_sequence_P00722():
    test_qualifier = "P00722"
    test_seq = "MTMITDSLAVVLQRRDWENPGVTQLNRLAAHPPFASWRNSEEARTDRPSQQLRSLNGEWRFAWFPAPEAVPESWLECDLPEADTVVVPSNWQMHGYDAPIYTNVTYPITVNPPFVPTENPTGCYSLTFNVDESWLQEGQTRIIFDGVNSAFHLWCNGRWVGYGQDSRLPSEFDLSAFLRAGENRLAVMVLRWSDGSYLEDQDMWRMSGIFRDVSLLHKPTTQISDFHVATRFNDDFSRAVLEAEVQMCGELRDYLRVTVSLWQGETQVASGTAPFGGEIIDERGGYADRVTLRLNVENPKLWSAEIPNLYRAVVELHTADGTLIEAEACDVGFREVRIENGLLLLNGKPLLIRGVNRHEHHPLHGQVMDEQTMVQDILLMKQNNFNAVRCSHYPNHPLWYTLCDRYGLYVVDEANIETHGMVPMNRLTDDPRWLPAMSERVTRMVQRDRNHPSVIIWSLGNESGHGANHDALYRWIKSVDPSRPVQYEGGGADTTATDIICPMYARVDEDQPFPAVPKWSIKKWLSLPGETRPLILCEYAHAMGNSLGGFAKYWQAFRQYPRLQGGFVWDWVDQSLIKYDENGNPWSAYGGDFGDTPNDRQFCMNGLVFADRTPHPALTEAKHQQQFFQFRLSGQTIEVTSEYLFRHSDNELLHWMVALDGKPLASGEVPLDVAPQGKQLIELPELPQPESAGQLWLTVRVVQPNATAWSEAGHISAWQQWRLAENLSVTLPAASHAIPHLTTSEMDFCIELGNKRWQFNRQSGFLSQMWIGDKKQLLTPLRDQFTRAPLDNDIGVSEATRIDPNAWVERWKAAGHYQAEAALLQCTADTLADAVLITTAHAWQHQGKTLFISRKTYRIDGSGQMAITVDVEVASDTPHPARIGLNCQLAQVAERVNWLGLGPQENYPDRLTAACFDRWDLPLSDMYTPYVFPSENGLRCGTRELNYGPHQWRGDFQFNISRYSQQQLMETSHRHLLHAEEGTWLNIDGFHMGIGGDDSWSPSVSAEFQLSAGRYHYQLVWCQK"  # noqa: E501
    test_get_sequence_res = get_alphafold_sequence(test_qualifier)
    assert test_seq == test_get_sequence_res["Sequence"]


def test_3D_model_redirect_P00722():
    response = client.get('/showstruct/P00722')
    assert response.url == 'https://alphafold.ebi.ac.uk/entry/P00722'


def test_3D_model_redirect_():
    response = client.get('/showstruct/P00420')
    assert response.url == 'https://alphafold.ebi.ac.uk/entry/P00420'


def test_predict_queue_task_1():
    test_seq = "MTHLERSRILWFRDIVAEATYLGDHTMFLNTIILAFTISDGVYGSVFYAGTGLHFLHMVMLAAMLGVNYWRMRNYHLTAGHHVGYETTIIYTHVLDVIWLFLYVVFYWWGV"  # noqa: E501
    result = predict_protein_structure.delay(test_seq)
    assert result.status == "PENDING"


def test_predict_queue_task_2():
    sequence = "IGVSEATRIDPNAWVERWKAAGHYQAEAALLQCTADTLADAVLITTAHAWQHQGKTLFISRKTYRIDGSGQMAITVDVEVASDTPHPARIGLNCQLAQVAERVNWLGLGPQENYPDRLTAACFDRWDLPLSDMYTPYVFPSENGLRCGTRELNYGPHQWRGDFQFNISRYSQQQLMETSHRHLLHAEEGTWLNIDGFHMGIGGDDSWSPSVSAEFQLSAGRYHYQ"  # noqa: E501
    result = predict_protein_structure.delay(sequence)
    assert result.status == "PENDING"


def test_get_status():
    sequence = "QHQGKTLFISRKTYRIDGSGQMAITVDVEVASDTPHPARIGLNCQLAQVAERVNWLGLGPQENYPDRLTAACFDRWDLPLSDMYTPYVFPSENGLRCGTRELNYGPHQWRGDFQFNISRYSQQQLMETSHRHLLHAEEGTWLNIDGFHMGIGGDDSWSPSVSAEFQ"  # noqa: E501
    result = async_predict(sequence)
    assert result["in_queue"]


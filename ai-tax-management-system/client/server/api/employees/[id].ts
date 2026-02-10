export default defineEventHandler(async (event): Promise<any> => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl || 'https://ai-hris-server.azurewebsites.net'
  const id = getRouterParam(event, 'id')
  const method = event.method

  const dummyEmployees =
  {
    "data": [
      {
        "address": {
          "city": "Jakarta Timur",
          "country": "Indonesia",
          "detail": "Jln. Pemuda No 101 Rawamangun",
          "zip": 161616
        },
        "employee_id": "84e62f5767d8-0337-440c-b2c5-d997e4e788890",
        "date_of_birth": "2000-06-20",
        "discrepancies": [
          {
            "category": "Location",
            "field": "Zip",
            "note": "ZIP codes differ significantly (161616 vs 335666)",
            "severity": "high",
            "source": {
              "name": "kartu_keluarga_siti_nurhaliza.png",
              "type": "KK",
              "value": "335666"
            },
            "target": {
              "name": "Applicant Data",
              "type": "Applicant Data",
              "value": "161616"
            }
          }
        ],
        "education": [
          {
            "degree": "Sarjana",
            "field_of_study": "Teknologi Informasi",
            "gpa": 3.6,
            "graduation_year": 2022,
            "institution": "Institut Teknologi Bandung"
          }
        ],
        "email": "agus.sulaiman@hotmail.com",
        "embeddings": [],
        "experience": 7.7,
        "family_members": [
          {
            "brief_data": {
              "contact": "+62-812-555-9090",
              "occupation": "Swasta"
            },
            "date_of_birth": "1990-05-15",
            "name": "Bambang Suseno",
            "relationship": "Husband"
          },
          {
            "brief_data": {
              "contact": "",
              "occupation": ""
            },
            "date_of_birth": "2025-09-04",
            "name": "Tisa",
            "relationship": "Daughter"
          }
        ],
        "gender": "Male",
        "id": "b2c5b2c5-6400-42b9-b9b0-ac8ee7ea6400",
        "joined_date": "2025-11-20T07:13:36.180340Z",
        "legalDocuments": [
          {
            "type": "KK",
            "name": "kartu_keluarga_siti_nurhaliza.png",
            "url": "https://protohub.blob.core.windows.net/hris/siti_nurhaliza/kartu_keluarga_siti_nurhaliza.png",
            "lastUpdated": "2025-11-25T07:16:04.742378Z",
            "extractedContent": {
              "boundingBoxes": [],
              "content": "KARTU KELUARGA No- 1000000000000000\nNama Kepala Keluarga Alamat RT/RW REPUBLIK INDONESIA Kode Pos\n: BAMBANG SUSENO\n: JALAN PEMUDA NO 105 RAWAMANGUN JAKARTA TIMUR\nDesa/Kelurahan Kecamatan : PULO GADUNG Kabupaten/Kota\nProvinsi\n: JAKARTA TIMUR : DKI JAKARTA\nNo\nNama Lengkap\nNIK\nJenis Kelamin\nTempat Lahir\nTanggal Lahir\nAgama\nPendidikan\nJenis Pekerjaan\nGolongan Darah\n(1)\n(2)\n(3)\n(4\n(5)\n(6)\n(7)\n(8)\n(9)\n1\nBAMBANG SUSENO\n1000000000000000\nLAKI-LAKI\nPONOROGO\n15-05-1990\nISLAM\nDIPLOMA IV/STRATA I\nSWASTA\n0\n2\nSITI NURHALIZA\n1000000000000333 |PEREMPUAN\nJAKARTA\n15-05-1992\nISLAM\nDIPLOMA IV/STRATA I\nSWASTA\n-\n4\n5\n6\n7\n-\nOC\n10\n-\n-\n-\nNo.\nStatus Perkawinan\nTanggal Perkawinan/Perceraian\nStatus Hubungan Dalam Keluarga\nKewarganegaraan\nNo. Paspor\nNo. KITAP\nAyah\nIbu\n(10)\n(11)\n(12)\n(13)\n(14)\n(15)\n(16)\n(17)\n1\nKAWIN TERCATAT\n14-02-2022\nKEPALA KELUARGA\nWNI\nSUKARJI\nSUTINI\n2\nKAWIN TERCATAT\n14-02-2022\nISTRI\nWNI\nADAM FAJAR\nENDANG RINI\n3\n4\n5\n6\n-\nF\n7\nF\n-\n#\n1\n1\n8\n9\n1\n-\n-\nF\n-\n10\n-\n-\n-\n-\n-\n-\n-\n1\nDikeluarkan Tanggal :\n12-10-2022\nKEPALA KELUARGA\nKEPALA DINAS KEPENDUDUKAN DAN PENCATATAN SIPIL\nSUHENDRO, SH.MM NIP. 196300000000000000\nBAMBANG SUSENO Tanda Tangan/Cap Jempol\nDokumen ini telah ditandatangani secara elektronik menggunakan sertifikat elektronik yang diterbitkan oleh Balai Sertifikasi Elektronik (BSrE), BSSN\n-\n-\n-\n-\nDokumen Imigrasi\nNama Orang Tua\n-\n-\n: PULO GADUNG\n: 003/001 : 335666\n3",
              "structuredData": {
                "address": "JALAN PEMUDA NO 105 RAWAMANGUN JAKARTA TIMUR",
                "city": "JAKARTA TIMUR",
                "district": "PULO GADUNG",
                "family_head_name": "BAMBANG SUSENO",
                "family_members": [
                  {
                    "birth_date": "1990-05-15",
                    "blood_type": "0",
                    "education": "DIPLOMA IV/STRATA I",
                    "gender": "LAKI-LAKI",
                    "marital_status": "KAWIN TERCATAT",
                    "name": "BAMBANG SUSENO",
                    "nik": "1000000000000000",
                    "occupation": "SWASTA",
                    "religion": "ISLAM"
                  },
                  {
                    "birth_date": "1992-05-15",
                    "blood_type": null,
                    "education": "DIPLOMA IV/STRATA I",
                    "gender": "PEREMPUAN",
                    "marital_status": "KAWIN TERCATAT",
                    "name": "SITI NURHALIZA",
                    "nik": "1000000000000333",
                    "occupation": "SWASTA",
                    "religion": "ISLAM"
                  }
                ],
                "family_number": "1000000000000000",
                "postal_code": "335666",
                "province": "DKI JAKARTA",
                "rt_rw": "003/001",
                "village": "PULO GADUNG"
              }
            }
          },
          {
            "type": "KTP",
            "name": "ktp_siti_nurhaliza.png",
            "url": "https://protohub.blob.core.windows.net/hris/siti_nurhaliza/kartu_keluarga_siti_nurhaliza.png",
            "lastUpdated": "2025-11-25T07:16:04.742378Z",
            "extractedContent": {
              "boundingBoxes": [],
              "content": "KARTU KELUARGA No- 1000000000000000\nNama Kepala Keluarga Alamat RT/RW REPUBLIK INDONESIA Kode Pos\n: BAMBANG SUSENO\n: JALAN PEMUDA NO 105 RAWAMANGUN JAKARTA TIMUR\nDesa/Kelurahan Kecamatan : PULO GADUNG Kabupaten/Kota\nProvinsi\n: JAKARTA TIMUR : DKI JAKARTA\nNo\nNama Lengkap\nNIK\nJenis Kelamin\nTempat Lahir\nTanggal Lahir\nAgama\nPendidikan\nJenis Pekerjaan\nGolongan Darah\n(1)\n(2)\n(3)\n(4\n(5)\n(6)\n(7)\n(8)\n(9)\n1\nBAMBANG SUSENO\n1000000000000000\nLAKI-LAKI\nPONOROGO\n15-05-1990\nISLAM\nDIPLOMA IV/STRATA I\nSWASTA\n0\n2\nSITI NURHALIZA\n1000000000000333 |PEREMPUAN\nJAKARTA\n15-05-1992\nISLAM\nDIPLOMA IV/STRATA I\nSWASTA\n-\n4\n5\n6\n7\n-\nOC\n10\n-\n-\n-\nNo.\nStatus Perkawinan\nTanggal Perkawinan/Perceraian\nStatus Hubungan Dalam Keluarga\nKewarganegaraan\nNo. Paspor\nNo. KITAP\nAyah\nIbu\n(10)\n(11)\n(12)\n(13)\n(14)\n(15)\n(16)\n(17)\n1\nKAWIN TERCATAT\n14-02-2022\nKEPALA KELUARGA\nWNI\nSUKARJI\nSUTINI\n2\nKAWIN TERCATAT\n14-02-2022\nISTRI\nWNI\nADAM FAJAR\nENDANG RINI\n3\n4\n5\n6\n-\nF\n7\nF\n-\n#\n1\n1\n8\n9\n1\n-\n-\nF\n-\n10\n-\n-\n-\n-\n-\n-\n-\n1\nDikeluarkan Tanggal :\n12-10-2022\nKEPALA KELUARGA\nKEPALA DINAS KEPENDUDUKAN DAN PENCATATAN SIPIL\nSUHENDRO, SH.MM NIP. 196300000000000000\nBAMBANG SUSENO Tanda Tangan/Cap Jempol\nDokumen ini telah ditandatangani secara elektronik menggunakan sertifikat elektronik yang diterbitkan oleh Balai Sertifikasi Elektronik (BSrE), BSSN\n-\n-\n-\n-\nDokumen Imigrasi\nNama Orang Tua\n-\n-\n: PULO GADUNG\n: 003/001 : 335666\n3",
              "structuredData": {
                "address": "JLN Pemuda 105 Rawamangun",
                "birth_date": "1992-05-15",
                "birth_place": "Jakarta",
                "city": "null",
                "district": "null",
                "gender": "Perempuan",
                "marital_status": "Kawin",
                "name": "Siti Nurhaliza",
                "nationality": "Indonesia",
                "nik": "1000000000000333",
                "occupation": "Swasta",
                "province": "null",
                "religion": "Islam",
                "rt_rw": "003/001",
                "village": "Pulo Gadung"
              }
            }
          }
        ],
        "name": "Agus Sulaiman",
        "phone": "+62-812-0505",
        "photo_url": "https://protohub.blob.core.windows.net/hris/siti_nurhaliza/Generated Image November 27, 2025 - 12_44PM.png",
        "position": "Software Engineer",
        "resume": {},
        "status": "active",
        "work_experiences": [
          {
            "company": "Tokopedia",
            "description": "Memimpin tim desain produk untuk fitur marketplace dan payment gateway",
            "end_date": null,
            "is_current": true,
            "position": "Senior Product Designer",
            "start_date": "2020-01-15"
          },
          {
            "company": "Grab",
            "description": "Mendesain interface pengguna untuk aplikasi mobile driver dan konsumen",
            "end_date": "2019-12-31",
            "is_current": false,
            "position": "Product Designer",
            "start_date": "2018-03-01"
          }
        ]
      }
    ],
    "message": "Employees retrieved successfully",
    "status": "Success"
  }
  if (!id) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Candidate ID is required',
    })
  }

  try {
    const fetchOptions: any = {
      method: method
    }

    if (method !== 'GET' && method !== 'HEAD') {
      fetchOptions.body = await readBody(event)
    }




    // const response: any = await $fetch<any>(`${apiUrl}/api/v1/hr/employee/${id}`, fetchOptions)
    const response: any = await dummyEmployees
    // Extract the data object from the response wrapper
    return response?.data || response
  } catch (error) {
    console.error(`Error ${method} candidate:`, error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to process candidate request',
    })
  }
})

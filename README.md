graph TD
    %% Define os nós (componentes)
    FE[Frontend (Mobile)]

    subgraph Django Backend
        direction TB
        Auth[App Auth<br/>- Views<br/>- Seriali.]
        OMOP[App OMOP<br/>- Models<br/>- Signals<br/>- Mappings]
    end

    subgraph PostgreSQL
        direction TB
        DB_User[auth_user<br/>(Django padrão)]
        DB_OMOP[omop_person<br/>(Padrão OMOP)]
    end

    %% Define as conexões (fluxo)
    FE -- "POST /auth/google/<br/>{ token, birth_date, gender }" --> Auth
    Auth -- "Cria User<br/>(Signal dispara)" --> OMOP
    
    %% Conexões com o Banco
    Auth --> DB_User
    OMOP --> DB_OMOP
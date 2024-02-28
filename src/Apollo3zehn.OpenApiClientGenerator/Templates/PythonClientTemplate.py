﻿{{#Special_NexusFeatures}}
class _Disposable{{{Async}}}Configuration:
    ___client : {{{ClientName}}}{{{Async}}}Client

    def __init__(self, client: {{{ClientName}}}{{{Async}}}Client):
        self.___client = client

    # "disposable" methods
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.___client.clear_configuration()
{{/Special_NexusFeatures}}

class {{{ClientName}}}{{{Async}}}Client:
    """A client for the {{{ClientName}}} system."""
    
{{#Special_NexusFeatures}}
    _configuration_header_key: str = "{{{ConfigurationHeaderKey}}}"
{{/Special_NexusFeatures}}
{{#Special_RefreshTokenSupport}}
    _authorization_header_key: str = "Authorization"

    _token_folder_path: str = os.path.join(str(Path.home()), "{{{TokenFolderName}}}", "tokens")
    _mutex: Lock = Lock()

    _token_pair: Optional[TokenPair]
    _token_file_path: Optional[str]
{{/Special_RefreshTokenSupport}}
    _http_client: {{{Async}}}Client

{{{SubClientFields}}}

    @classmethod
    def create(cls, base_url: str) -> {{{ClientName}}}{{{Async}}}Client:
        """
        Initializes a new instance of the {{{ClientName}}}{{{Async}}}Client
        
            Args:
                base_url: The base URL to use.
        """
        return {{{ClientName}}}{{{Async}}}Client({{{Async}}}Client(base_url=base_url, timeout=60.0))

    def __init__(self, http_client: {{{Async}}}Client):
        """
        Initializes a new instance of the {{{ClientName}}}{{{Async}}}Client
        
            Args:
                http_client: The HTTP client to use.
        """

        if http_client.base_url is None:
            raise Exception("The base url of the HTTP client must be set.")

        self._http_client = http_client
        self._token_pair = None

{{{SubClientFieldAssignments}}}

{{#Special_RefreshTokenSupport}}
    @property
    def is_authenticated(self) -> bool:
        """Gets a value which indicates if the user is authenticated."""
        return self._token_pair is not None
{{/Special_RefreshTokenSupport}}

{{{SubClientProperties}}}

{{#Special_RefreshTokenSupport}}
    {{{Def}}} sign_in(self, refresh_token: str):
        """Signs in the user.

        Args:
            token_pair: The refresh token.
        """

        actual_refresh_token: str

        sha256 = hashlib.sha256()
        sha256.update(refresh_token.encode())
        refresh_token_hash = sha256.hexdigest()
        self._token_file_path = os.path.join(self._token_folder_path, refresh_token_hash + ".json")
        
        if Path(self._token_file_path).is_file():
            with open(self._token_file_path) as file:
                actual_refresh_token = file.read()

        else:
            Path(self._token_folder_path).mkdir(parents=True, exist_ok=True)

            with open(self._token_file_path, "w") as file:
                file.write(refresh_token)
                actual_refresh_token = refresh_token
                
        {{{Await}}}self._refresh_token(actual_refresh_token)
{{/Special_RefreshTokenSupport}}

{{#Special_NexusFeatures}}
    def attach_configuration(self, configuration: Any) -> Any:
        """Attaches configuration data to subsequent API requests.
        
        Args:
            configuration: The configuration data.
        """

        encoded_json = base64.b64encode(json.dumps(configuration).encode("utf-8")).decode("utf-8")

        if self._configuration_header_key in self._http_client.headers:
            del self._http_client.headers[self._configuration_header_key]

        self._http_client.headers[self._configuration_header_key] = encoded_json

        return _Disposable{{{Async}}}Configuration(self)

    def clear_configuration(self) -> None:
        """Clears configuration data for all subsequent API requests."""

        if self._configuration_header_key in self._http_client.headers:
            del self._http_client.headers[self._configuration_header_key]
{{/Special_NexusFeatures}}

    {{{Def}}} _invoke(self, typeOfT: Optional[Type[T]], method: str, relative_url: str, accept_header_value: Optional[str], content_type_value: Optional[str], content: Union[None, str, bytes, Iterable[bytes], AsyncIterable[bytes]]) -> T:

        # prepare request
        request = self._build_request_message(method, relative_url, content, content_type_value, accept_header_value)

        # send request
        response = {{{Await}}}self._http_client.send(request)

        # process response
        if not response.is_success:
            
{{#Special_RefreshTokenSupport}}
            # try to refresh the access token
            if response.status_code == codes.UNAUTHORIZED and self._token_pair is not None:

                www_authenticate_header = response.headers.get("WWW-Authenticate")
                sign_out = True

                if www_authenticate_header is not None:

                    if "The token expired at" in www_authenticate_header:

                        try:
                            {{{Await}}}self._refresh_token(self._token_pair.refresh_token)

                            new_request = self._build_request_message(method, relative_url, content, content_type_value, accept_header_value)
                            new_response = {{{Await}}}self._http_client.send(new_request)

                            {{{Await}}}response.{{{Aclose}}}()
                            response = new_response
                            sign_out = False

                        except:
                            pass

                if sign_out:
                    self._sign_out()
{{/Special_RefreshTokenSupport}}

            if not response.is_success:

                message = response.text
                status_code = f"{{{ExceptionCodePrefix}}}00.{response.status_code}"

                if not message:
                    raise {{{ExceptionType}}}(status_code, f"The HTTP request failed with status code {response.status_code}.")

                else:
                    raise {{{ExceptionType}}}(status_code, f"The HTTP request failed with status code {response.status_code}. The response message is: {message}")

        try:

            if typeOfT is type(None):
                return cast(T, type(None))

            elif typeOfT is Response:
                return cast(T, response)

            else:

                jsonObject = json.loads(response.text)
                return_value = JsonEncoder.decode(cast(Type[T], typeOfT), jsonObject, _json_encoder_options)

                if return_value is None:
                    raise {{{ExceptionType}}}("{{{ExceptionCodePrefix}}}01", "Response data could not be deserialized.")

                return return_value

        finally:
            if typeOfT is not Response:
                {{{Await}}}response.{{{Aclose}}}()
    
    def _build_request_message(self, method: str, relative_url: str, content: Any, content_type_value: Optional[str], accept_header_value: Optional[str]) -> Request:
       
        request_message = self._http_client.build_request(method, relative_url, content = content)

        if content_type_value is not None:
            request_message.headers["Content-Type"] = content_type_value

        if accept_header_value is not None:
            request_message.headers["Accept"] = accept_header_value

        return request_message

{{#Special_RefreshTokenSupport}}
    {{{Def}}} _refresh_token(self, refresh_token: str):
        self._mutex.acquire()

        try:
            # make sure the refresh token has not already been redeemed
            if (self._token_pair is not None and refresh_token != self._token_pair.refresh_token):
                return

            # see https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/blob/dev/src/Microsoft.IdentityModel.Tokens/Validators.cs#L390

            refresh_request = RefreshTokenRequest(refresh_token)
            token_pair = {{{Await}}}self.users.refresh_token(refresh_request)

            if self._token_file_path is not None:
                Path(self._token_folder_path).mkdir(parents=True, exist_ok=True)
                
                with open(self._token_file_path, "w") as file:
                    file.write(token_pair.refresh_token)

            authorizationHeaderValue = f"Bearer {token_pair.access_token}"

            if self._authorization_header_key in self._http_client.headers:
                del self._http_client.headers[self._authorization_header_key]

            self._http_client.headers[self._authorization_header_key] = authorizationHeaderValue
            self._token_pair = token_pair

        finally:
            self._mutex.release()

    def _sign_out(self) -> None:

        if self._authorization_header_key in self._http_client.headers:
            del self._http_client.headers[self._authorization_header_key]

        self._token_pair = None
{{/Special_RefreshTokenSupport}}

    # "disposable" methods
    {{{Def}}} __{{{Enter}}}__(self) -> {{{ClientName}}}{{{Async}}}Client:
        return self

    {{{Def}}} __{{{Exit}}}__(self, exc_type, exc_value, exc_traceback):
        if (self._http_client is not None):
            {{{Await}}}self._http_client.{{{Aclose}}}()

{{#Special_NexusFeatures}}
    {{{Def}}} load(
        self,
        begin: datetime, 
        end: datetime, 
        resource_paths: Iterable[str],
        on_progress: Optional[Callable[[float], None]]) -> dict[str, DataResponse]:
        """This high-level methods simplifies loading multiple resources at once.

        Args:
            begin: Start date/time.
            end: End date/time.
            resource_paths: The resource paths.
            onProgress: A callback which accepts the current progress.
        """

        catalog_item_map = {{{Await}}}self.catalogs.search_catalog_items(list(resource_paths))
        result: dict[str, DataResponse] = {}
        progress: float = 0

        for (resource_path, catalog_item) in catalog_item_map.items():

            response = {{{Await}}}self.data.get_stream(resource_path, begin, end)

            try:
                double_data = {{{Await}}}self._read_as_double(response)

            finally:
                {{{Await}}}response.{{{Aclose}}}()

            resource = catalog_item.resource

            unit = cast(str, resource.properties["unit"]) \
                if resource.properties is not None and "unit" in resource.properties and type(resource.properties["unit"]) == str \
                else None

            description = cast(str, resource.properties["description"]) \
                if resource.properties is not None and "description" in resource.properties and type(resource.properties["description"]) == str \
                else None

            sample_period = catalog_item.representation.sample_period

            result[resource_path] = DataResponse(
                catalog_item=catalog_item,
                name=resource.id,
                unit=unit,
                description=description,
                sample_period=sample_period,
                values=double_data
            )

            progress = progress + 1.0 / len(catalog_item_map)

            if on_progress is not None:
                on_progress(progress)
                
        return result

    {{{Def}}} _read_as_double(self, response: Response):
        
        byteBuffer = {{{Await}}}response.{{{Read}}}()

        if len(byteBuffer) % 8 != 0:
            raise Exception("The data length is invalid.")

        doubleBuffer = array("d", byteBuffer)

        return doubleBuffer 

    {{{Def}}} export(
        self,
        begin: datetime, 
        end: datetime, 
        file_period: timedelta,
        file_format: Optional[str],
        resource_paths: Iterable[str],
        configuration: dict[str, object],
        target_folder: str,
        on_progress: Optional[Callable[[float, str], None]]) -> None:
        """This high-level methods simplifies exporting multiple resources at once.

        Args:
            begin: Start date/time.
            end: End date/time.
            filePeriod: The file period. Use timedelta(0) to get a single file.
            fileFormat: The target file format. If null, data will be read (and possibly cached) but not returned. This is useful for data pre-aggregation.
            resource_paths: The resource paths to export.
            configuration: The configuration.
            targetFolder: The target folder for the files to extract.
            onProgress: A callback which accepts the current progress and the progress message.
        """

        export_parameters = ExportParameters(
            begin,
            end,
            file_period,
            file_format,
            list(resource_paths),
            configuration
        )

        # Start job
        job = {{{Await}}}self.jobs.export(export_parameters)

        # Wait for job to finish
        artifact_id: Optional[str] = None

        while True:
            {{{Await}}}{{{AsyncioSleep}}}(1)
            
            job_status = {{{Await}}}self.jobs.get_job_status(job.id)

            if (job_status.status == TaskStatus.CANCELED):
                raise Exception("The job has been cancelled.")

            elif (job_status.status == TaskStatus.FAULTED):
                raise Exception(f"The job has failed. Reason: {job_status.exception_message}")

            elif (job_status.status == TaskStatus.RAN_TO_COMPLETION):

                if (job_status.result is not None and \
                    type(job_status.result) == str):

                    artifact_id = cast(Optional[str], job_status.result)

                    break

            if job_status.progress < 1 and on_progress is not None:
                on_progress(job_status.progress, "export")

        if on_progress is not None:
            on_progress(1, "export")

        if artifact_id is None:
            raise Exception("The job result is invalid.")

        if file_format is None:
            return

        # Download zip file
        with NamedTemporaryFile() as target_stream:

            response = {{{Await}}}self.artifacts.download(artifact_id)
            
            try:

                length: Optional[int] = None

                try:
                    length = int(response.headers["Content-Length"])
                except:
                    pass

                consumed = 0.0

                {{{For}}} data in response.{{{Aiter_bytes}}}():

                    target_stream.write(data)
                    consumed += len(data)

                    if length is not None and on_progress is not None:
                        if consumed < length:
                            on_progress(consumed / length, "download")

            finally:
                {{{Await}}}response.{{{Aclose}}}()

            if on_progress is not None:
                on_progress(1, "download")

            # Extract file
            with ZipFile(target_stream, "r") as zipFile:
                zipFile.extractall(target_folder)

        if on_progress is not None:
            on_progress(1, "extract")
{{/Special_NexusFeatures}}